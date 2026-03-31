"""IMDb client for charts and custom lists."""

import asyncio
import re
from typing import Optional

from imdb import Cinemagoer
from loguru import logger


_CHART_METHOD: dict[str, str] = {
    "moviemeter": "get_popular100_movies",
    "tvmeter": "get_popular100_tv",
    "top": "get_top250_movies",
    "boxoffice": "get_boxoffice",
}


class IMDbClient:
    """Client for fetching IMDb chart/list title IDs via cinemagoer."""

    async def get_chart(self, chart_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a chart."""
        chart_key = chart_id.strip().lower()
        method_name = _CHART_METHOD.get(chart_key)
        if not method_name:
            logger.warning(f"[IMDb] Unknown chart '{chart_id}'")
            return []

        try:
            ia = Cinemagoer()
            method = getattr(ia, method_name)
            items = await asyncio.to_thread(method)
        except Exception as exc:
            logger.warning(f"[IMDb] Chart {chart_key}: failed — {exc}")
            return []

        ids = [f"tt{item.movieID.zfill(7)}" for item in (items or [])[:limit]]
        logger.info(f"[IMDb] Chart {chart_key}: fetched {len(ids)} ids")
        return ids

    async def get_list(self, list_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a custom list (ls...)."""
        normalized = self._extract_list_id(list_id)
        if not normalized:
            logger.warning(f"[IMDb] Invalid list id '{list_id}'")
            return []

        try:
            ia = Cinemagoer()
            items = await asyncio.to_thread(ia.get_imdblist, normalized)
        except Exception as exc:
            logger.warning(f"[IMDb] List {normalized}: failed — {exc}")
            return []

        ids = [f"tt{item.movieID.zfill(7)}" for item in (items or [])[:limit]]
        logger.info(f"[IMDb] List {normalized}: fetched {len(ids)} ids")
        return ids

    def _extract_list_id(self, value: str) -> Optional[str]:
        """Extract ls* list id from raw string or IMDb URL."""
        raw = value.strip()
        if re.fullmatch(r"ls\d+", raw):
            return raw
        match = re.search(r"/list/(ls\d+)", raw)
        if match:
            return match.group(1)
        return None

    async def __aenter__(self) -> "IMDbClient":
        return self

    async def __aexit__(self, *args) -> None:
        pass
