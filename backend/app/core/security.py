import hmac
import hashlib
import time
from typing import Optional
from urllib.parse import parse_qsl
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from app.core.config import get_settings

settings = get_settings()

def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """Verifies Telegram WebApp initData exactly per Telegram's documented algorithm."""
    try:
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
        if "hash" not in parsed_data:
            return False
            
        hash_value = parsed_data.pop("hash")
        
        # Reject if auth_date is older than 24h
        if "auth_date" in parsed_data:
            auth_date = int(parsed_data["auth_date"])
            if time.time() - auth_date > 86400:
                return False
        
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )
        
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return computed_hash == hash_value
    except Exception:
        return False


def create_session_token(user_id: str) -> str:
    header = {"alg": "HS256"}
    payload = {
        "sub": str(user_id),
        "iat": int(time.time()),
        "exp": int(time.time()) + 30 * 86400  # ~30 day TTL
    }
    return jwt.encode(header, payload, settings.SECRET_KEY).decode("utf-8")

def verify_session_token(token: str) -> Optional[str]:
    try:
        claims = jwt.decode(token, settings.SECRET_KEY)
        claims.validate()
        return str(claims["sub"])
    except JoseError:
        return None
    except Exception:
        return None
