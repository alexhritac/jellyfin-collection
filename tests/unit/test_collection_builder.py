"""Unit tests for collection builder filtering and list helpers."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from jfc.models.collection import CollectionConfig, CollectionFilter
from jfc.models.media import MediaType, Movie, Series
from jfc.services.collection_builder import CollectionBuilder


@pytest.fixture
def builder() -> CollectionBuilder:
    """Create a collection builder with mocked clients."""
    jellyfin = MagicMock()
    tmdb = MagicMock()
    return CollectionBuilder(jellyfin=jellyfin, tmdb=tmdb, dry_run=True)


def test_apply_filters_excludes_genre_names(builder: CollectionBuilder) -> None:
    """Genre-name exclusions should work for providers like Trakt."""
    items = [
        Movie(title="True Crime Story", genres=["crime", "drama"]),
        Movie(title="Adventure Time", genres=["adventure"]),
    ]
    config = CollectionConfig(
        name="No Crime",
        filters=CollectionFilter(without_genres=["crime"]),
    )

    filtered = builder._apply_filters(items, config)

    assert [item.title for item in filtered] == ["Adventure Time"]


def test_apply_filters_matches_hyphenated_genres(builder: CollectionBuilder) -> None:
    """Genre matching should normalize hyphens and case."""
    items = [Movie(title="Future World", genres=["science-fiction"])]
    config = CollectionConfig(
        name="Sci-Fi Only",
        filters=CollectionFilter(with_genres=["Science Fiction"]),
    )

    filtered = builder._apply_filters(items, config)

    assert [item.title for item in filtered] == ["Future World"]


@pytest.mark.asyncio
async def test_fetch_trakt_list_uses_user_and_slug() -> None:
    """Trakt list references should fetch items via the Trakt client."""
    jellyfin = MagicMock()
    tmdb = MagicMock()
    trakt = MagicMock()
    trakt.get_list = AsyncMock(
        return_value=[Series(title="Example Show", genres=["documentary"], media_type=MediaType.SERIES)]
    )
    builder = CollectionBuilder(jellyfin=jellyfin, tmdb=tmdb, trakt=trakt, dry_run=True)

    items = await builder._fetch_trakt_list("alice/favorites", MediaType.SERIES)

    trakt.get_list.assert_awaited_once_with(
        user="alice",
        list_id="favorites",
        media_type=MediaType.SERIES,
    )
    assert [item.title for item in items] == ["Example Show"]


def test_parse_trakt_list_ref_supports_url(builder: CollectionBuilder) -> None:
    """Full Trakt list URLs should parse into user and slug."""
    parsed = builder._parse_trakt_list_ref("https://trakt.tv/users/alice/lists/favorites")

    assert parsed == ("alice", "favorites")
