from __future__ import annotations
import io
import logging
from pathlib import Path
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import httpx
from PIL import Image

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])
logger = logging.getLogger(__name__)

# Base upload directory
UPLOAD_DIR = Path("uploads/logos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def process_image_to_webp(content: bytes, max_size: int = 512) -> bytes:
    """Resize image to fit within max_size x max_size and encode to WebP."""
    img = Image.open(io.BytesIO(content))
    img = img.convert("RGBA")
    
    # Resize preserving aspect ratio or square
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    out_io = io.BytesIO()
    img.save(out_io, format="WEBP", quality=88, method=6)
    return out_io.getvalue()


@router.post("/logo")
async def upload_logo(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """Upload and optimize a logo image for a listing (WebP 512px)."""
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES and not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Faqat rasm fayllari (PNG, JPG, WebP, GIF) qabul qilinadi"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Rasm hajmi 5 MB dan oshmasligi kerak"
        )

    try:
        webp_bytes = process_image_to_webp(content, max_size=512)
    except Exception as e:
        logger.warning("Image processing failed: %s", e)
        raise HTTPException(status_code=400, detail="Yaroqsiz rasm formati")

    filename = f"{uuid.uuid4().hex}.webp"
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as f:
        f.write(webp_bytes)

    return {"url": f"/api/v1/uploads/logos/{filename}"}


@router.get("/logos/{filename}")
async def get_logo(filename: str):
    """Serve uploaded logo image with caching."""
    # Prevent path traversal
    safe_name = Path(filename).name
    file_path = UPLOAD_DIR / safe_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Rasm topilmadi")

    return FileResponse(
        file_path,
        media_type="image/webp",
        headers={"Cache-Control": "public, max-age=31536000, immutable"}
    )


async def fetch_and_save_telegram_avatar(handle: str) -> str | None:
    """Fetch avatar of a public Telegram channel and save as WebP logo."""
    settings = get_settings()
    if not settings.BOT_TOKEN:
        return None

    clean_handle = handle.strip().lstrip("@")
    if not clean_handle:
        return None

    proper_handle = f"@{clean_handle}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(
                f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getChat",
                params={"chat_id": proper_handle}
            )
            if not res.is_success:
                return None
            data = res.json()
            if not data.get("ok"):
                return None

            chat = data.get("result", {})
            photo = chat.get("photo")
            if not photo or not photo.get("big_file_id"):
                return None

            file_id = photo["big_file_id"]
            file_res = await client.get(
                f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile",
                params={"file_id": file_id}
            )
            if not file_res.is_success:
                return None
            file_data = file_res.json()
            if not file_data.get("ok") or not file_data.get("result", {}).get("file_path"):
                return None

            tg_file_path = file_data["result"]["file_path"]
            img_res = await client.get(
                f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{tg_file_path}"
            )
            if not img_res.is_success:
                return None

            # Convert to WebP 512px
            webp_bytes = process_image_to_webp(img_res.content, max_size=512)
            filename = f"tg_{clean_handle}_{uuid.uuid4().hex[:8]}.webp"
            dest_path = UPLOAD_DIR / filename
            with open(dest_path, "wb") as f:
                f.write(webp_bytes)

            return f"/api/v1/uploads/logos/{filename}"
    except Exception as e:
        logger.warning("Failed to fetch Telegram channel avatar for %s: %s", proper_handle, e)
        return None
