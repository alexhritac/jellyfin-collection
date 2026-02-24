"""Unit tests for IMDb client."""

from unittest.mock import AsyncMock

import pytest

from jfc.clients.imdb import IMDbClient


class _HtmlResponse:
    """Minimal HTML response wrapper for tests."""

    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.mark.asyncio
async def test_get_list_returns_empty_on_404() -> None:
    """IMDb list fetch should return empty list on 404."""
    client = IMDbClient()
    client.get = AsyncMock(return_value=_HtmlResponse(404))

    ids = await client.get_list("ls000000001")

    assert ids == []


def test_extract_imdb_ids_dedup_preserves_order() -> None:
    """Title ID extraction should deduplicate while preserving first occurrence."""
    client = IMDbClient()
    html = (
        '<a href="/title/tt0111161/">A</a>'
        '<a href="/title/tt0068646/">B</a>'
        '<a href="/title/tt0111161/">A2</a>'
    )

    ids = client._extract_imdb_ids(html)

    assert ids == ["tt0111161", "tt0068646"]


def test_extract_imdb_ids_from_next_data() -> None:
    """Extraction should prefer IMDb __NEXT_DATA__ payload when present."""
    client = IMDbClient()
    html = """
<html>
  <head>
    <script id="__NEXT_DATA__" type="application/json">
      {"props":{"pageProps":{"ids":["tt1234567","tt7654321","tt1234567"]}}}
    </script>
  </head>
</html>
"""

    ids = client._extract_imdb_ids(html)

    assert ids == ["tt1234567", "tt7654321"]
