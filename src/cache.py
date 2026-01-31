"""Cache module for storing Apify Store data as a local database with ML scores."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import httpx
from apify import Actor

from .categories import CATEGORIES

if TYPE_CHECKING:
    from .classifier import CategoryClassifier


# Named Key-Value Store for persistence across runs
KV_STORE_NAME = "apify-store-searcher-cache"
CACHE_ACTORS_KEY = "actor_database"
CACHE_METADATA_KEY = "cache_metadata"


@dataclass
class ActorDatabase:
    """Local database of all actors with pre-computed ML scores."""

    actors: list[dict] = field(default_factory=list)
    last_updated: float = 0.0
    total_fetched: int = 0


class StoreCache:
    """
    Cache for Apify Store data using Apify Key-Value Store for persistence.

    Fetches ALL actors from the store, computes ML scores once, and stores
    everything locally. Search and category filtering happen in-memory.
    """

    # Cache settings
    FETCH_LIMIT = 1000  # API limit per request
    REFRESH_INTERVAL = 300  # Refresh every 5 minutes
    API_TIMEOUT = 60.0

    def __init__(self):
        self._db = ActorDatabase()
        self._category_index: dict[str, list[int]] = {}  # category -> actor indices
        self._classifier: CategoryClassifier | None = None
        self._initialized = False

    def set_classifier(self, classifier: CategoryClassifier) -> None:
        """Set the classifier for ML ranking."""
        self._classifier = classifier

    async def initialize(self) -> None:
        """Initialize cache - load from Key-Value Store or fetch fresh data."""
        if self._initialized:
            return

        Actor.log.info("Loading Actor database from Key-Value Store...")

        # Try to load from Key-Value Store first
        loaded = await self._load_from_kv_store()

        if loaded:
            Actor.log.info(f"Database loaded: {len(self._db.actors)} actors")
            self._build_category_index()
            # Check if cache is stale and needs refresh
            if self._is_cache_stale():
                Actor.log.info("Database is stale, refreshing in background...")
                asyncio.create_task(self._refresh_database())
        else:
            Actor.log.info("No cached data found, fetching fresh data...")
            await self._refresh_database()

        self._initialized = True

    async def _load_from_kv_store(self) -> bool:
        """Load database from Apify Key-Value Store."""
        try:
            kv_store = await Actor.open_key_value_store(name=KV_STORE_NAME)

            # Load metadata
            metadata = await kv_store.get_value(CACHE_METADATA_KEY)
            if not metadata:
                return False

            # Load actor database
            data = await kv_store.get_value(CACHE_ACTORS_KEY)
            if not data or not data.get("actors"):
                return False

            self._db = ActorDatabase(
                actors=data.get("actors", []),
                last_updated=data.get("last_updated", 0),
                total_fetched=data.get("total_fetched", 0),
            )

            return len(self._db.actors) > 0

        except Exception as e:
            Actor.log.warning(f"Failed to load database from KV Store: {e}")
            return False

    async def _save_to_kv_store(self) -> None:
        """Save database to Apify Key-Value Store."""
        try:
            kv_store = await Actor.open_key_value_store(name=KV_STORE_NAME)

            # Save actor database
            await kv_store.set_value(
                CACHE_ACTORS_KEY,
                {
                    "actors": self._db.actors,
                    "last_updated": self._db.last_updated,
                    "total_fetched": self._db.total_fetched,
                },
            )

            # Save metadata
            await kv_store.set_value(
                CACHE_METADATA_KEY,
                {
                    "last_refresh": time.time(),
                    "actor_count": len(self._db.actors),
                },
            )

            Actor.log.debug("Database saved to Key-Value Store")

        except Exception as e:
            Actor.log.warning(f"Failed to save database to KV Store: {e}")

    def _is_cache_stale(self) -> bool:
        """Check if the cache is stale and needs refresh."""
        if not self._db.actors:
            return True

        age = time.time() - self._db.last_updated
        return age > self.REFRESH_INTERVAL

    def _build_category_index(self) -> None:
        """Build index mapping categories to actor indices for fast filtering."""
        self._category_index = {cat: [] for cat in CATEGORIES}

        for idx, actor in enumerate(self._db.actors):
            # Get actor's categories
            categories = actor.get("categories", [])
            if isinstance(categories, list):
                for cat in categories:
                    cat_id = cat.get("id") if isinstance(cat, dict) else cat
                    if cat_id in self._category_index:
                        self._category_index[cat_id].append(idx)

    async def _refresh_database(self) -> None:
        """Fetch all actors from API and rebuild the database."""
        Actor.log.info("Fetching all Actors from Apify Store API...")

        all_actors: list[dict] = []
        seen_ids: set[str] = set()
        total_in_store = 0

        async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
            # Fetch actors without category filter - paginate through ALL
            offset = 0
            while True:
                try:
                    response = await client.get(
                        "https://api.apify.com/v2/store",
                        params={"limit": self.FETCH_LIMIT, "offset": offset},
                    )
                    response.raise_for_status()
                    data = response.json()

                    items = data.get("data", {}).get("items", [])
                    total_in_store = data.get("data", {}).get("total", 0)

                    if not items:
                        break

                    # Deduplicate by actor ID
                    for actor in items:
                        actor_id = actor.get("id")
                        if actor_id and actor_id not in seen_ids:
                            seen_ids.add(actor_id)
                            all_actors.append(actor)

                    Actor.log.info(f"Fetched {len(all_actors)}/{total_in_store} Actors...")

                    # Check if we've fetched all
                    if offset + len(items) >= total_in_store:
                        break

                    offset += self.FETCH_LIMIT

                except Exception as e:
                    Actor.log.warning(f"Error fetching Actors at offset {offset}: {e}")
                    break

        Actor.log.info(f"Fetched {len(all_actors)} unique Actors from API (total in store: {total_in_store})")

        # Apply ML scoring if classifier is available (preserve original order)
        if self._classifier and all_actors:
            Actor.log.info("Computing ML scores for all Actors...")
            all_actors = self._classifier.rerank_actors(all_actors, category_filter=None, sort=False)
            Actor.log.info("ML scoring complete")

        # Update database
        self._db = ActorDatabase(
            actors=all_actors,
            last_updated=time.time(),
            total_fetched=len(all_actors),
        )

        # Build category index
        self._build_category_index()

        # Save to Key-Value Store
        await self._save_to_kv_store()

        Actor.log.info(f"Database refresh complete: {len(all_actors)} Actors cached")

    def get_actors(
        self,
        category: str = "",
        search: str = "",
        use_ranked: bool = True,
    ) -> tuple[list[dict], int]:
        """
        Get actors from the local database.

        Args:
            category: Category filter (empty for all)
            search: Search query to filter by title/description
            use_ranked: Whether to return ML-ranked results

        Returns:
            Tuple of (actors list, total count)
        """
        if not self._db.actors:
            return [], 0

        # Start with all actors or filter by category
        if category and category in self._category_index:
            indices = self._category_index[category]
            actors = [self._db.actors[i] for i in indices]
        else:
            actors = self._db.actors.copy()

        # Apply search filter
        if search:
            search_lower = search.lower()
            actors = [
                actor for actor in actors
                if search_lower in (actor.get("title") or "").lower()
                or search_lower in (actor.get("description") or "").lower()
                or search_lower in (actor.get("username") or "").lower()
            ]

        # Sort by ML rank score if available and requested
        if use_ranked:
            actors = sorted(
                actors,
                key=lambda x: x.get("_ml_rank_score", 0),
                reverse=True,
            )

        return actors, len(actors)

    def get_actors_for_category_ranked(self, category: str) -> list[dict]:
        """
        Get actors for a category, ranked by the pre-computed category-specific ML score.

        Uses the _ml_scores dict that was computed during cache refresh,
        so this is instant (no re-computation needed).
        """
        if not self._db.actors or not category:
            return []

        if category not in self._category_index:
            return []

        indices = self._category_index[category]
        actors = [self._db.actors[i] for i in indices]

        # Sort by the pre-computed category-specific ML score
        actors = sorted(
            actors,
            key=lambda x: x.get("_ml_scores", {}).get(category, 0),
            reverse=True,
        )

        return actors

    def is_cache_fresh(self) -> bool:
        """Check if the cache is fresh."""
        if not self._db.actors:
            return False
        age = time.time() - self._db.last_updated
        return age < self.REFRESH_INTERVAL

    def get_cache_stats(self) -> dict:
        """Get statistics about the cache."""
        return {
            "total_actors": len(self._db.actors),
            "total_fetched": self._db.total_fetched,
            "last_updated": self._db.last_updated,
            "age_seconds": time.time() - self._db.last_updated
            if self._db.last_updated > 0
            else None,
            "categories": {
                cat: len(indices) for cat, indices in self._category_index.items()
            },
        }

    async def start_background_refresh(self) -> None:
        """Start background refresh loop."""
        while True:
            await asyncio.sleep(self.REFRESH_INTERVAL)
            try:
                await self._refresh_database()
            except Exception as e:
                Actor.log.warning(f"Background refresh error: {e}")


# Global cache instance
store_cache = StoreCache()
