"""Unit tests for the Redis cache manager, backed by ``fakeredis``."""
from unittest.mock import patch

import fakeredis
import pytest


@pytest.fixture
def redis_cache():
    """Build a ``RedisCacheManager`` whose underlying client is a fakeredis instance."""
    from frontegg.common.cache.redis_cache_manager import RedisCacheManager

    fake = fakeredis.FakeStrictRedis()

    class FakeRedisModule:
        Redis = lambda **kwargs: fake  # noqa: E731

    with patch(
        "frontegg.common.package_utils.PackageUtils.load_package",
        return_value=FakeRedisModule,
    ):
        yield RedisCacheManager(
            {"host": "h", "port": 6379, "db": 0, "password": "pw"}
        )


class TestRedisCacheManager:
    def test_set_and_get(self, redis_cache):
        redis_cache.set("k", {"v": 1})
        assert redis_cache.get("k") == {"v": 1}

    def test_get_missing_returns_none(self, redis_cache):
        assert redis_cache.get("missing") is None

    def test_set_with_ttl(self, redis_cache):
        # fakeredis supports expire(); just assert no crash and value readable.
        redis_cache.set("k", [1, 2, 3], {"expires_in_seconds": 60})
        assert redis_cache.get("k") == [1, 2, 3]
