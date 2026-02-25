"""Unit tests for TMDb client."""

from unittest.mock import AsyncMock

import pytest

from jfc.clients.tmdb import TMDbClient


class _NotFoundResponse:
    """Minimal response object for 404 simulations."""

    status_code = 404

    def raise_for_status(self) -> None:
        raise AssertionError("raise_for_status should not be called on 404 branch")

    def json(self) -> dict:
        return {}


@pytest.mark.asyncio
async def test_get_list_returns_empty_on_404() -> None:
    """TMDb list fetch should return empty list on 404."""
    client = TMDbClient(api_key="test-api-key")
    client.get = AsyncMock(return_value=_NotFoundResponse())

    items = await client.get_list(8232)

    assert items == []
    client.get.assert_awaited_once()



class _JsonResponse:
    """Minimal JSON response object for TMDb client tests."""

    def __init__(self, data: dict, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._data


@pytest.mark.asyncio
async def test_find_by_imdb_id_returns_movie() -> None:
    """TMDb find endpoint should resolve a movie result."""
    client = TMDbClient(api_key="test-api-key")
    client.get = AsyncMock(
        return_value=_JsonResponse(
            {
                "movie_results": [{"id": 13, "title": "Forrest Gump", "release_date": "1994-07-06"}],
                "tv_results": [],
            }
        )
    )

    item = await client.find_by_imdb_id("tt0109830")

    assert item is not None
    assert item.tmdb_id == 13
    assert item.imdb_id == "tt0109830"
