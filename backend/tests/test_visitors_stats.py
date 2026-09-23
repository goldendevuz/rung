import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.api.v1.routes.stats import get_visitors_stats

@pytest.mark.asyncio
async def test_get_visitors_stats_not_configured():
    with patch("app.api.v1.routes.stats.get_settings") as mock_settings:
        mock_settings.return_value.DATAFAST_API_KEY = ""
        result = await get_visitors_stats()
        assert result.configured is False
        assert result.visitors_today is None
        assert result.visitors_30d is None

@pytest.mark.asyncio
async def test_get_visitors_stats_configured():
    mock_30d = httpx.Response(200, json={"visitors": 142}, request=httpx.Request("GET", "https://datafa.st"))
    mock_today = httpx.Response(200, json={"visitors": 12}, request=httpx.Request("GET", "https://datafa.st"))

    async def mock_get(url, **kwargs):
        if "startAt=" in str(url) and str(url).count("202") == 2:
            # Check if start and end are same day
            parts = str(url).split("startAt=")[1].split("&endAt=")
            if parts[0] == parts[1]:
                return mock_today
        return mock_30d

    with patch("app.api.v1.routes.stats.get_settings") as mock_settings, \
         patch("app.api.v1.routes.stats.get_redis", return_value=None), \
         patch("httpx.AsyncClient.get", side_effect=mock_get):
        mock_settings.return_value.DATAFAST_API_KEY = "df_test_key"
        result = await get_visitors_stats()
        assert result.configured is True
        assert result.visitors_30d == 142
        assert result.visitors_today == 12

@pytest.mark.asyncio
async def test_get_visitors_stats_list_format():
    mock_30d = httpx.Response(200, json={"status": "success", "data": [{"visitors": 65}]}, request=httpx.Request("GET", "https://datafa.st"))
    mock_today = httpx.Response(200, json={"status": "success", "data": [{"visitors": 57}]}, request=httpx.Request("GET", "https://datafa.st"))

    async def mock_get(url, **kwargs):
        if "startAt=" in str(url) and str(url).count("202") == 2:
            parts = str(url).split("startAt=")[1].split("&endAt=")
            if parts[0] == parts[1]:
                return mock_today
        return mock_30d

    with patch("app.api.v1.routes.stats.get_settings") as mock_settings, \
         patch("app.api.v1.routes.stats.get_redis", return_value=None), \
         patch("httpx.AsyncClient.get", side_effect=mock_get):
        mock_settings.return_value.DATAFAST_API_KEY = "df_test_key"
        result = await get_visitors_stats()
        assert result.configured is True
        assert result.visitors_30d == 65
        assert result.visitors_today == 57

