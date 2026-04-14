"""Unit tests for the in-memory cache manager."""
import time

from frontegg.common.cache.local_cache_manager import LocalCacheManager


class TestLocalCacheManager:
    def test_set_and_get_without_expiry(self):
        cache = LocalCacheManager()
        cache.set("key", {"v": 1})
        assert cache.get("key") == {"v": 1}

    def test_get_missing_key_returns_none(self):
        cache = LocalCacheManager()
        assert cache.get("nope") is None

    def test_set_with_ttl_returns_value_before_expiry(self):
        cache = LocalCacheManager()
        cache.set("k", "v", {"expires_in_seconds": 60})
        assert cache.get("k") == "v"

    def test_set_with_ttl_expires(self):
        cache = LocalCacheManager()
        cache.set("k", "v", {"expires_in_seconds": 0.01})
        time.sleep(0.02)
        assert cache.get("k") is None
        assert "k" not in cache.cache  # deleted on expiry

    def test_delete_removes_keys(self):
        cache = LocalCacheManager()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.delete(["a", "missing"])
        assert cache.get("a") is None
        assert cache.get("b") == 2

    def test_overwrite_replaces_value(self):
        cache = LocalCacheManager()
        cache.set("k", "first")
        cache.set("k", "second")
        assert cache.get("k") == "second"
