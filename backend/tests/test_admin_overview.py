import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.api.v1.routes.users import get_admin_users_overview
from app.models.user import User
from app.models.listing import Listing
import uuid

@pytest.mark.asyncio
async def test_admin_overview_forbidden_without_token():
    mock_db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await get_admin_users_overview(
            db=mock_db,
            x_internal_token=None,
            secret_key=None,
        )
    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_admin_overview_authorized_internal_token():
    mock_db = AsyncMock()
    u1 = User()
    u1.id = uuid.uuid4()
    u1.telegram_id = 557407324
    u1.username = "goldendevuz"
    u1.first_name = "Admin"
    u1.balance = 495
    u1.is_admin = True

    l1 = Listing()
    l1.id = uuid.uuid4()
    l1.name = "My Channel"
    l1.handle = "@my_channel"
    l1.status = "active"
    l1.subscribers = 500
    l1.owner_id = u1.id

    res1 = MagicMock()
    res1.scalars.return_value = [u1]
    res2 = MagicMock()
    res2.scalars.return_value = [l1]
    res3 = MagicMock()
    res3.scalars.return_value = []
    res4 = MagicMock()
    res4.scalars.return_value = []

    calls = [res1, res2, res3, res4]
    async def mock_execute(*args, **kwargs):
        return calls.pop(0)

    mock_db.execute = mock_execute

    with patch("app.api.v1.routes.users.settings") as mock_settings:
        mock_settings.INTERNAL_API_TOKEN = "test_token"
        mock_settings.SECRET_KEY = "test_secret"

        result = await get_admin_users_overview(
            db=mock_db,
            x_internal_token="test_token",
        )
        assert result["total_users"] == 1
        assert result["total_listings"] == 1
        assert result["users"][0]["telegram_id"] == 557407324
        assert result["users"][0]["balance_b"] == 495
        assert "total_deposited_b" in result["users"][0]
        assert "total_spent_b" in result["users"][0]
        assert len(result["users"][0]["listings"]) == 1
        assert result["users"][0]["listings"][0]["handle"] == "@my_channel"

@pytest.mark.asyncio
async def test_admin_overview_caller_tg_id_unauthorized():
    mock_db = AsyncMock()
    # Mock caller user who is NOT admin
    u_non_admin = User()
    u_non_admin.is_admin = False
    res_caller = MagicMock()
    res_caller.scalar_one_or_none.return_value = u_non_admin

    mock_db.execute = AsyncMock(return_value=res_caller)

    with patch("app.api.v1.routes.users.settings") as mock_settings:
        mock_settings.INTERNAL_API_TOKEN = "test_token"
        mock_settings.SECRET_KEY = "test_secret"

        with pytest.raises(HTTPException) as exc_info:
            await get_admin_users_overview(
                db=mock_db,
                x_internal_token="test_token",
                caller_tg_id=12345678,
            )
        assert exc_info.value.status_code == 403
