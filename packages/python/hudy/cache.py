"""Smart caching with year-based TTL."""

import time
from datetime import date, datetime
from typing import Dict, List, Optional

from .types import CacheStats, Holiday


class CacheEntry:
    """Cache entry with expiration."""

    def __init__(self, data: List[Holiday], expires_at: float):
        self.data = data
        self.expires_at = expires_at


class SmartCache:
    """Smart cache with year-based TTL."""

    def __init__(self, custom_ttl: Optional[int] = None):
        self._store: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
        self._custom_ttl = custom_ttl  # User-provided override in seconds

    def get(self, year: int) -> Optional[List[Holiday]]:
        """Get cached holidays for a year."""
        key = self._get_year_key(year)
        entry = self._store.get(key)

        if not entry:
            self._misses += 1
            return None

        # Check if expired
        if time.time() > entry.expires_at:
            del self._store[key]
            self._misses += 1
            return None

        self._hits += 1
        return entry.data

    def set(self, year: int, holidays: List[Holiday]) -> None:
        """Store holidays for a year with appropriate TTL."""
        key = self._get_year_key(year)
        ttl = self._get_ttl(year)
        expires_at = time.time() + ttl

        self._store[key] = CacheEntry(holidays, expires_at)

    def get_range(self, from_date: date, to_date: date) -> Optional[List[Holiday]]:
        """
        Get cached holidays for a date range.
        Returns None if any required year is not fully cached.
        Note: Client now fetches by year and filters, so this may not be used directly.
        """
        from_year = from_date.year
        to_year = to_date.year

        from_str = from_date.strftime("%Y-%m-%d")
        to_str = to_date.strftime("%Y-%m-%d")

        # If single year, just check that year's cache
        if from_year == to_year:
            cached = self.get(from_year)
            if not cached:
                return None

            # Filter by date range
            return [h for h in cached if from_str <= h.date <= to_str]

        # Multi-year range: need all years cached
        all_holidays: List[Holiday] = []
        for year in range(from_year, to_year + 1):
            cached = self.get(year)
            if not cached:
                # Don't increment misses again - get() already did it
                return None
            all_holidays.extend(cached)

        # Don't increment hits again - the get() calls already did it
        return [h for h in all_holidays if from_str <= h.date <= to_str]

    def clear(self) -> None:
        """Clear all cached data."""
        self._store.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            size=len(self._store),
            entries=[
                {"key": key, "expiresAt": entry.expires_at}
                for key, entry in self._store.items()
            ],
        )

    def prune(self) -> int:
        """Remove expired entries (garbage collection)."""
        now = time.time()
        to_remove = [
            key for key, entry in self._store.items() if now > entry.expires_at
        ]

        for key in to_remove:
            del self._store[key]

        return len(to_remove)

    # Private helpers

    def _get_year_key(self, year: int) -> str:
        """Get cache key for a year."""
        return f"year:{year}"

    def _get_ttl(self, year: int) -> int:
        """Get TTL in seconds based on year."""
        # If user provided custom TTL, use it
        if self._custom_ttl is not None:
            return self._custom_ttl

        # Otherwise use year-based logic
        current_year = datetime.now().year

        if year < current_year:
            # Past: 1 year (very stable)
            return 365 * 24 * 60 * 60
        elif year == current_year:
            # Current: 1 day (may change)
            return 24 * 60 * 60
        else:
            # Future: 1 week (not finalized)
            return 7 * 24 * 60 * 60
