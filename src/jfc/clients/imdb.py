"""IMDb client for charts and custom lists."""

import re
from typing import Optional

from loguru import logger

from jfc.clients.base import BaseClient


class IMDbClient(BaseClient):
    """Client for fetching IMDb chart/list title IDs."""

    BASE_URL = "https://www.imdb.com"

    CHART_PATHS = {
        "top": "/chart/top/",
        "boxoffice": "/chart/boxoffice/",
        "moviemeter": "/chart/moviemeter/",
        "tvmeter": "/chart/tvmeter/",
    }

    def __init__(self):
        super().__init__(
            base_url=self.BASE_URL,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "User-Agent": "Mozilla/5.0 (compatible; jfc/1.0)",
            },
        )

    async def get_chart(self, chart_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a chart endpoint."""
        chart_key = chart_id.strip().lower()
        path = self.CHART_PATHS.get(chart_key)
        if not path:
            logger.warning(f"Unknown IMDb chart '{chart_id}'")
            return []

        response = await self.get(path)
        if response.status_code == 404:
            logger.warning(f"IMDb chart not found: {chart_id}")
            return []

        response.raise_for_status()
        imdb_ids = self._extract_imdb_ids(response.text, limit=limit)
        logger.info(f"[IMDb] Chart {chart_key}: fetched {len(imdb_ids)} ids")
        return imdb_ids

    async def get_list(self, list_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a custom list (ls...)."""
        normalized = self._extract_list_id(list_id)
        if not normalized:
            logger.warning(f"Invalid IMDb list id '{list_id}'")
            return []

        response = await self.get(f"/list/{normalized}/")
        if response.status_code == 404:
            logger.warning(f"IMDb list not found: {normalized}")
            return []

        response.raise_for_status()
        imdb_ids = self._extract_imdb_ids(response.text, limit=limit)
        logger.info(f"[IMDb] List {normalized}: fetched {len(imdb_ids)} ids")
        return imdb_ids

    def _extract_list_id(self, value: str) -> Optional[str]:
        """Extract ls* list id from raw string or IMDb URL."""
        raw = value.strip()
        if re.fullmatch(r"ls\d+", raw):
            return raw

        match = re.search(r"/list/(ls\d+)", raw)
        if match:
            return match.group(1)

        return None

    def _extract_imdb_ids(self, html: str, limit: int = 250) -> list[str]:
        """Extract unique tt* IDs from HTML in first-seen order."""
        seen: set[str] = set()
        ids: list[str] = []

        for match in re.finditer(r"/title/(tt\d{7,9})", html):
            imdb_id = match.group(1)
            if imdb_id in seen:
                continue
            seen.add(imdb_id)
            ids.append(imdb_id)
            if len(ids) >= limit:
                break

        return ids
