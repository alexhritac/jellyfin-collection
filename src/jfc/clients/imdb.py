"""IMDb client for charts and custom lists."""

import json
import re
from typing import Optional

from loguru import logger
from playwright.async_api import Browser, Playwright, async_playwright


class IMDbClient:
    """Client for fetching IMDb chart/list title IDs via headless Chromium."""

    BASE_URL = "https://www.imdb.com"

    CHART_PATHS = {
        "top": "/chart/top/",
        "boxoffice": "/chart/boxoffice/",
        "moviemeter": "/chart/moviemeter/",
        "tvmeter": "/chart/tvmeter/",
    }

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    async def _get_browser(self) -> Browser:
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
        return self._browser

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def _fetch_html(self, url: str) -> Optional[str]:
        browser = await self._get_browser()
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30_000)
            return await page.content()
        except Exception as exc:
            logger.warning(f"[IMDb] Failed to fetch {url}: {exc}")
            return None
        finally:
            await page.close()

    async def get_chart(self, chart_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a chart endpoint."""
        chart_key = chart_id.strip().lower()
        path = self.CHART_PATHS.get(chart_key)
        if not path:
            logger.warning(f"[IMDb] Unknown chart '{chart_id}'")
            return []

        html = await self._fetch_html(self.BASE_URL + path)
        if not html:
            return []

        imdb_ids = self._extract_imdb_ids(html, limit=limit)
        logger.info(f"[IMDb] Chart {chart_key}: fetched {len(imdb_ids)} ids")
        return imdb_ids

    async def get_list(self, list_id: str, limit: int = 250) -> list[str]:
        """Get IMDb title IDs from a custom list (ls...)."""
        normalized = self._extract_list_id(list_id)
        if not normalized:
            logger.warning(f"[IMDb] Invalid list id '{list_id}'")
            return []

        html = await self._fetch_html(f"{self.BASE_URL}/list/{normalized}/")
        if not html:
            return []

        imdb_ids = self._extract_imdb_ids(html, limit=limit)
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
