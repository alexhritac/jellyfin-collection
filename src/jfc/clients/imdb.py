"""IMDb client for charts and custom lists."""

import json
import re
from typing import Optional

from curl_cffi.requests import AsyncSession
from loguru import logger


class IMDbClient:
    """Client for fetching IMDb chart/list title IDs."""

    BASE_URL = "https://m.imdb.com"

    CHART_PATHS = {
        "top": "/chart/top/",
        "boxoffice": "/chart/boxoffice/",
        "moviemeter": "/chart/moviemeter/",
        "tvmeter": "/chart/tvmeter/",
    }

    def __init__(self):
        self._session: Optional[AsyncSession] = None

    async def _get_session(self) -> AsyncSession:
        if self._session is None:
            self._session = AsyncSession(impersonate="safari_ios")
        return self._session

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def get_chart(self, chart_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a chart endpoint."""
        chart_key = chart_id.strip().lower()
        path = self.CHART_PATHS.get(chart_key)
        if not path:
            logger.warning(f"[IMDb] Unknown chart '{chart_id}'")
            return []

        session = await self._get_session()
        response = await session.get(self.BASE_URL + path)

        if response.status_code == 404:
            logger.warning(f"[IMDb] Chart not found: {chart_id}")
            return []

        if response.status_code != 200:
            logger.warning(
                f"[IMDb] Chart {chart_key}: received HTTP {response.status_code} "
                "(likely challenge response)"
            )
            return []

        imdb_ids = self._extract_imdb_ids(response.text, limit=limit)
        logger.info(f"[IMDb] Chart {chart_key}: fetched {len(imdb_ids)} ids")
        return imdb_ids

    async def get_list(self, list_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a custom list (ls...)."""
        normalized = self._extract_list_id(list_id)
        if not normalized:
            logger.warning(f"[IMDb] Invalid list id '{list_id}'")
            return []

        session = await self._get_session()
        response = await session.get(f"{self.BASE_URL}/list/{normalized}/")

        if response.status_code == 404:
            logger.warning(f"[IMDb] List not found: {normalized}")
            return []

        if response.status_code != 200:
            logger.warning(
                f"[IMDb] List {normalized}: received HTTP {response.status_code} "
                "(likely challenge response)"
            )
            return []

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
        """Extract unique tt* IDs from IMDb HTML in first-seen order."""
        next_data_ids = self._extract_imdb_ids_from_next_data(html, limit=limit)
        if next_data_ids:
            return next_data_ids

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

    def _extract_imdb_ids_from_next_data(self, html: str, limit: int = 250) -> list[str]:
        """Extract IDs from IMDb __NEXT_DATA__ payload when present."""
        match = re.search(
            r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL,
        )
        if not match:
            return []

        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return []

        seen: set[str] = set()
        ids: list[str] = []

        def walk(value: object) -> None:
            if len(ids) >= limit:
                return

            if isinstance(value, str):
                if re.fullmatch(r"tt\d{7,9}", value) and value not in seen:
                    seen.add(value)
                    ids.append(value)
                return

            if isinstance(value, list):
                for item in value:
                    walk(item)
                    if len(ids) >= limit:
                        break
                return

            if isinstance(value, dict):
                for item in value.values():
                    walk(item)
                    if len(ids) >= limit:
                        break

        walk(payload)
        return ids

    async def __aenter__(self) -> "IMDbClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
