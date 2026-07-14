"""Unit tests for the ``FronteggContext`` singleton and its option validation."""
import pytest

from frontegg.common.frontegg_context import FronteggContext


class TestFronteggContext:
    def test_is_singleton(self):
        a = FronteggContext()
        b = FronteggContext()
        assert a is b

    def test_init_stores_options(self):
        FronteggContext.init({"foo": "bar"})
        assert FronteggContext().options == {"foo": "bar"}

    def test_init_without_access_tokens_options_is_ok(self):
        FronteggContext.init({})  # must not raise
        assert FronteggContext().options == {}

    def test_init_rejects_missing_cache_in_access_tokens_options(self):
        with pytest.raises(Exception, match="cache"):
            FronteggContext.init({"access_tokens_options": {}})

    def test_local_cache_is_accepted(self):
        FronteggContext.init(
            {"access_tokens_options": {"cache": {"type": "local"}}}
        )
        assert FronteggContext().options["access_tokens_options"]["cache"]["type"] == "local"

    def test_redis_cache_requires_all_properties(self):
        bad = {
            "access_tokens_options": {
                "cache": {
                    "type": "redis",
                    "options": {"host": "h", "port": 6379, "db": 0},  # missing password
                }
            }
        }
        with pytest.raises(Exception, match="password"):
            FronteggContext.init(bad)

    def test_redis_cache_full_options_accepted(self):
        good = {
            "access_tokens_options": {
                "cache": {
                    "type": "redis",
                    "options": {
                        "host": "h",
                        "port": 6379,
                        "db": 0,
                        "password": "pw",
                    },
                }
            }
        }
        FronteggContext.init(good)  # must not raise
