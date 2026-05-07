import httpx
import pytest
import respx

from imdbapi.client import IMDBAPIClient
from imdbapi.exceptions import IMDBAPIValidationError

BASE_URL = "https://api.imdbapi.dev"


@pytest.fixture
def client() -> IMDBAPIClient:
    return IMDBAPIClient(base_url=BASE_URL, max_retries=1)


@pytest.mark.asyncio
async def test_starmeter_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/chart/starmeter").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.charts.starmeter()
