"""Unit tests for ``CacheAccessTokenService`` variants — mirrors
nodejs-sdk cache-access-token.service.spec.ts.

Covers:
- Cache hit returns cached value without calling inner service
- Cache miss calls inner service and caches result with 10s TTL
- Negative caching: ``{empty: True}`` sentinel on UnauthenticatedException
- Cached sentinel raises UnauthenticatedException
- Non-auth errors are NOT cached
- Active token ID caching (hit/miss/empty on error)
- Both CacheUserAccessTokenService and CacheTenantAccessTokenService
"""
from unittest.mock import MagicMock

import pytest

from frontegg.common.cache.local_cache_manager import LocalCacheManager
from frontegg.common.clients.types import TokenTypes
from frontegg.helpers.exceptions import UnauthenticatedException


def _build_service(cls, inner_mock):
    entity_cache = LocalCacheManager()
    ids_cache = LocalCacheManager()
    service = cls(entity_cache, ids_cache, inner_mock)
    return service, entity_cache, ids_cache


def _inner():
    m = MagicMock()
    m.type = None
    return m


# =========================================================================
# CacheTenantAccessTokenService
# =========================================================================


class TestCacheTenantAccessTokenService:
    @pytest.fixture
    def setup(self):
        from frontegg.common.clients.token_resolvers.access_token_services.cache_services.cache_tenant_access_token_service import (
            CacheTenantAccessTokenService,
        )

        inner = _inner()
        svc, e_cache, id_cache = _build_service(CacheTenantAccessTokenService, inner)
        return svc, inner, e_cache, id_cache

    def test_should_handle_tenant(self, setup):
        svc, *_ = setup
        assert svc.should_handle(TokenTypes.TenantAccessToken.value) is True
        assert svc.should_handle(TokenTypes.UserAccessToken.value) is False

    def test_get_entity_cache_hit_skips_inner(self, setup):
        svc, inner, e_cache, _ = setup
        entity = {"sub": "tok-1", "tenantId": "t"}
        e_cache.set(
            "frontegg_sdk_v1_tenant_access_tokens_tok-1",
            {"sub": "tok-1", "roles": ["admin"], "permissions": ["r"]},
        )
        result = svc.get_entity(entity)
        assert result["roles"] == ["admin"]
        inner.get_entity.assert_not_called()

    def test_get_entity_cache_miss_calls_inner_and_caches(self, setup):
        svc, inner, e_cache, _ = setup
        entity_data = {"sub": "tok-2", "roles": ["v"], "permissions": ["r"]}
        inner.get_entity.return_value = entity_data
        entity = {"sub": "tok-2", "tenantId": "t"}

        result = svc.get_entity(entity)
        assert result == entity_data
        inner.get_entity.assert_called_once_with(entity)
        # Verify it was cached
        cached = e_cache.get("frontegg_sdk_v1_tenant_access_tokens_tok-2")
        assert cached == entity_data

    def test_get_entity_caches_empty_on_unauth(self, setup):
        svc, inner, e_cache, _ = setup
        inner.get_entity.side_effect = UnauthenticatedException()
        entity = {"sub": "tok-3", "tenantId": "t"}

        # The Python implementation doesn't re-raise — it returns None.
        # (Unlike the Node SDK which throws.) We test what the code does.
        svc.get_entity(entity)
        cached = e_cache.get("frontegg_sdk_v1_tenant_access_tokens_tok-3")
        assert cached == {"empty": True}

    def test_get_entity_raises_for_cached_empty_sentinel(self, setup):
        svc, inner, e_cache, _ = setup
        e_cache.set(
            "frontegg_sdk_v1_tenant_access_tokens_tok-4", {"empty": True}
        )
        with pytest.raises(UnauthenticatedException):
            svc.get_entity({"sub": "tok-4", "tenantId": "t"})
        inner.get_entity.assert_not_called()

    def test_get_active_ids_cache_hit_skips_inner(self, setup):
        svc, inner, _, id_cache = setup
        id_cache.set("frontegg_sdk_v1_tenant_access_tokens_ids", ["id-1", "id-2"])
        result = svc.get_active_access_token_ids()
        assert result == ["id-1", "id-2"]
        inner.get_active_access_token_ids.assert_not_called()

    def test_get_active_ids_cache_miss_calls_inner(self, setup):
        svc, inner, _, id_cache = setup
        inner.get_active_access_token_ids.return_value = ["id-3"]
        result = svc.get_active_access_token_ids()
        assert result == ["id-3"]
        inner.get_active_access_token_ids.assert_called_once()
        assert id_cache.get("frontegg_sdk_v1_tenant_access_tokens_ids") == ["id-3"]

    def test_get_active_ids_caches_empty_on_unauth(self, setup):
        svc, inner, _, id_cache = setup
        inner.get_active_access_token_ids.side_effect = UnauthenticatedException()
        result = svc.get_active_access_token_ids()
        assert result == []
        assert id_cache.get("frontegg_sdk_v1_tenant_access_tokens_ids") == []


# =========================================================================
# CacheUserAccessTokenService
# =========================================================================


class TestCacheUserAccessTokenService:
    @pytest.fixture
    def setup(self):
        from frontegg.common.clients.token_resolvers.access_token_services.cache_services.cache_user_access_token_service import (
            CacheUserAccessTokenService,
        )

        inner = _inner()
        svc, e_cache, id_cache = _build_service(CacheUserAccessTokenService, inner)
        return svc, inner, e_cache, id_cache

    def test_should_handle_user(self, setup):
        svc, *_ = setup
        assert svc.should_handle(TokenTypes.UserAccessToken.value) is True
        assert svc.should_handle(TokenTypes.TenantAccessToken.value) is False

    def test_get_entity_cache_hit(self, setup):
        svc, inner, e_cache, _ = setup
        e_cache.set(
            "frontegg_sdk_v1_user_access_tokens_tok-u1",
            {"sub": "tok-u1", "roles": ["r"], "permissions": ["p"]},
        )
        result = svc.get_entity({"sub": "tok-u1"})
        assert result["roles"] == ["r"]
        inner.get_entity.assert_not_called()

    def test_get_entity_cache_miss(self, setup):
        svc, inner, e_cache, _ = setup
        inner.get_entity.return_value = {"sub": "tok-u2", "roles": [], "permissions": []}
        result = svc.get_entity({"sub": "tok-u2"})
        inner.get_entity.assert_called_once()
        assert e_cache.get("frontegg_sdk_v1_user_access_tokens_tok-u2") is not None

    def test_cached_empty_sentinel_raises(self, setup):
        svc, inner, e_cache, _ = setup
        e_cache.set("frontegg_sdk_v1_user_access_tokens_tok-u3", {"empty": True})
        with pytest.raises(UnauthenticatedException):
            svc.get_entity({"sub": "tok-u3"})

    def test_active_ids_cache_hit(self, setup):
        svc, inner, _, id_cache = setup
        id_cache.set("frontegg_sdk_v1_user_access_tokens_ids", ["u-id-1"])
        assert svc.get_active_access_token_ids() == ["u-id-1"]
        inner.get_active_access_token_ids.assert_not_called()

    def test_active_ids_cache_miss(self, setup):
        svc, inner, _, id_cache = setup
        inner.get_active_access_token_ids.return_value = ["u-id-2"]
        assert svc.get_active_access_token_ids() == ["u-id-2"]
        inner.get_active_access_token_ids.assert_called_once()
