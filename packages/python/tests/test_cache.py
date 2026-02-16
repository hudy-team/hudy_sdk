"""SmartCache tests."""
from hudy.cache import SmartCache

from .helpers import MOCK_HOLIDAYS_2024


class TestSmartCache:
    """Test suite for SmartCache."""

    def test_basic_set_and_get(self):
        """Test basic cache storage and retrieval."""
        cache = SmartCache()
        cache.set(2024, MOCK_HOLIDAYS_2024)

        retrieved = cache.get(2024)
        assert retrieved == MOCK_HOLIDAYS_2024

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = SmartCache()
        retrieved = cache.get(2024)
        assert retrieved is None

    def test_overwrite_entry(self):
        """Test overwriting existing cache entry."""
        cache = SmartCache()
        first_data = [MOCK_HOLIDAYS_2024[0]]
        second_data = MOCK_HOLIDAYS_2024

        cache.set(2024, first_data)
        cache.set(2024, second_data)

        retrieved = cache.get(2024)
        assert retrieved == second_data

    def test_multiple_years(self):
        """Test caching multiple years."""
        cache = SmartCache()
        holidays_2023 = [MOCK_HOLIDAYS_2024[0]]
        holidays_2024 = MOCK_HOLIDAYS_2024

        cache.set(2023, holidays_2023)
        cache.set(2024, holidays_2024)

        assert cache.get(2023) == holidays_2023
        assert cache.get(2024) == holidays_2024

    def test_expiration_future_year(self):
        """Test expiration for future years."""
        cache = SmartCache()
        from datetime import datetime
        future_year = datetime.now().year + 1

        cache.set(future_year, MOCK_HOLIDAYS_2024)

        stats = cache.get_stats()
        entry = next((e for e in stats.entries if e["key"] == f"year:{future_year}"), None)

        assert entry is not None
        assert entry["expiresAt"] > int(datetime.now().timestamp())

    def test_expiration_past_year(self):
        """Test expiration for past years (long TTL)."""
        cache = SmartCache()
        from datetime import datetime
        past_year = 2020

        cache.set(past_year, MOCK_HOLIDAYS_2024)

        stats = cache.get_stats()
        entry = next((e for e in stats.entries if e["key"] == f"year:{past_year}"), None)

        assert entry is not None
        # Past years should have very long expiration (365 days)
        one_year_from_now = int(datetime.now().timestamp() + 365 * 24 * 60 * 60)
        assert entry["expiresAt"] >= one_year_from_now - 1

    def test_expired_entry_returns_none(self):
        """Test that expired entries return None."""
        cache = SmartCache()
        cache.set(2024, MOCK_HOLIDAYS_2024)

        # Manually expire the entry
        cache._store["year:2024"].expires_at = 0

        retrieved = cache.get(2024)
        assert retrieved is None

    def test_expired_entry_auto_removed(self):
        """Test that expired entries are auto-removed on get."""
        cache = SmartCache()
        cache.set(2024, MOCK_HOLIDAYS_2024)

        # Manually expire the entry
        cache._store["year:2024"].expires_at = 0

        cache.get(2024)  # Should remove expired entry

        stats = cache.get_stats()
        assert stats.size == 0

    def test_cache_hit_tracking(self):
        """Test cache hit tracking."""
        cache = SmartCache()
        cache.set(2024, MOCK_HOLIDAYS_2024)

        cache.get(2024)  # Hit
        cache.get(2024)  # Hit

        stats = cache.get_stats()
        assert stats.hits == 2

    def test_cache_miss_tracking(self):
        """Test cache miss tracking."""
        cache = SmartCache()

        cache.get(2024)  # Miss
        cache.get(2025)  # Miss

        stats = cache.get_stats()
        assert stats.misses == 2

    def test_cache_size_tracking(self):
        """Test cache size tracking."""
        cache = SmartCache()

        cache.set(2023, MOCK_HOLIDAYS_2024)
        cache.set(2024, MOCK_HOLIDAYS_2024)
        cache.set(2025, MOCK_HOLIDAYS_2024)

        stats = cache.get_stats()
        assert stats.size == 3

    def test_cache_entries_list(self):
        """Test cache entries list in stats."""
        cache = SmartCache()

        cache.set(2024, MOCK_HOLIDAYS_2024)
        cache.set(2025, MOCK_HOLIDAYS_2024)

        stats = cache.get_stats()
        assert len(stats.entries) == 2
        assert all("key" in entry for entry in stats.entries)
        assert all("expiresAt" in entry for entry in stats.entries)

    def test_clear_cache(self):
        """Test clearing all cache entries."""
        cache = SmartCache()

        cache.set(2023, MOCK_HOLIDAYS_2024)
        cache.set(2024, MOCK_HOLIDAYS_2024)
        cache.set(2025, MOCK_HOLIDAYS_2024)

        cache.clear()

        stats = cache.get_stats()
        assert stats.size == 0
        assert cache.get(2024) is None

    def test_clear_resets_stats(self):
        """Test that clear resets statistics."""
        cache = SmartCache()

        cache.set(2024, MOCK_HOLIDAYS_2024)
        cache.get(2024)  # Hit
        cache.get(2025)  # Miss

        cache.clear()

        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0

    def test_prune_expired_entries(self):
        """Test pruning expired entries."""
        cache = SmartCache()

        cache.set(2024, MOCK_HOLIDAYS_2024)
        cache.set(2025, MOCK_HOLIDAYS_2024)

        # Expire one entry
        cache._store["year:2024"].expires_at = 0

        pruned = cache.prune()
        assert pruned == 1

        stats = cache.get_stats()
        assert stats.size == 1
        assert cache.get(2024) is None
        assert cache.get(2025) is not None

    def test_prune_no_expired(self):
        """Test pruning with no expired entries."""
        cache = SmartCache()
        cache.set(2024, MOCK_HOLIDAYS_2024)

        pruned = cache.prune()
        assert pruned == 0

    def test_empty_holiday_list(self):
        """Test caching empty holiday list."""
        cache = SmartCache()
        cache.set(2024, [])

        retrieved = cache.get(2024)
        assert retrieved == []

    def test_year_boundaries(self):
        """Test years at boundaries."""
        cache = SmartCache()

        cache.set(1900, MOCK_HOLIDAYS_2024)
        cache.set(2100, MOCK_HOLIDAYS_2024)

        assert cache.get(1900) == MOCK_HOLIDAYS_2024
        assert cache.get(2100) == MOCK_HOLIDAYS_2024

    def test_data_not_mutated(self):
        """Test that cached data is not mutated."""
        cache = SmartCache()
        original_data = MOCK_HOLIDAYS_2024.copy()

        cache.set(2024, MOCK_HOLIDAYS_2024)
        retrieved = cache.get(2024)

        # Ensure original is unchanged
        assert MOCK_HOLIDAYS_2024 == original_data
        assert retrieved == original_data
