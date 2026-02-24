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
