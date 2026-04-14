"""Unit tests for ``UserAccessTokenService`` and ``TenantAccessTokenService``.

Mirrors nodejs-sdk user-access-token.service.spec.ts and
tenant-access-token.service.spec.ts.

Covers:
- shouldHandle routing per token type
- getEntity calls correct identity endpoint
- getActiveAccessTokenIds calls correct endpoint
- "Api tokens are disabled" 403 error → UnauthenticatedException
"""
from unittest.mock import MagicMock

import pytest

from frontegg.common.clients.types import TokenTypes
from frontegg.helpers.exceptions import UnauthenticatedException


def _mock_http_client():
    return MagicMock(name="HttpClient")


def _make_response(json_data=None, status_code=200, text=None):
    resp = MagicMock()
    resp.json.return_value = json_data or {}
    resp.status_code = status_code
    resp.raise_for_status.return_value = None
    resp.text = text or ""
    return resp


def _make_403_api_tokens_disabled():
    import json
    resp = MagicMock()
    resp.status_code = 403
    resp.text = json.dumps({"errors": ["Api tokens are disabled"]})
    resp.response = resp  # for nested attribute access in __is_api_tokens_disabled

    exc = Exception("HTTP 403")
    exc.response = resp
    resp.raise_for_status.side_effect = exc
    return resp, exc


# =========================================================================
# UserAccessTokenService
# =========================================================================

class TestUserAccessTokenService:
    @pytest.fixture
    def service(self):
        from frontegg.common.clients.token_resolvers.access_token_services.services.user_access_token_service import (
            UserAccessTokenService,
        )
        http = _mock_http_client()
        return UserAccessTokenService(http), http

    def test_should_handle_user_access_token(self, service):
        svc, _ = service
        assert svc.should_handle(TokenTypes.UserAccessToken.value) is True
        assert svc.should_handle(TokenTypes.TenantAccessToken.value) is False

    def test_get_entity_from_identity_calls_correct_endpoint(self, service):
        svc, http = service
        http.get.return_value = _make_response(
            {"roles": ["viewer"], "permissions": ["read"]}
        )
        entity = {"sub": "tok-u1", "tenantId": "t"}
        result = svc.get_entity_from_identity(entity)

        url_called = http.get.call_args[0][0]
        assert "users/access-tokens/v1/" in url_called
        assert result["roles"] == ["viewer"]
        assert result["permissions"] == ["read"]

    def test_get_active_token_ids_calls_correct_endpoint(self, service):
        svc, http = service
        http.get.return_value = _make_response(["id-1", "id-2"])
        result = svc.get_active_access_token_ids_from_identity()

        url_called = http.get.call_args[0][0]
        assert "users/access-tokens/v1/active" in url_called
        assert result == ["id-1", "id-2"]

    def test_api_tokens_disabled_raises_unauthenticated(self, service):
        svc, http = service
        _, exc = _make_403_api_tokens_disabled()
        http.get.side_effect = exc

        with pytest.raises(UnauthenticatedException):
            svc.get_entity({"sub": "tok-u"})


# =========================================================================
# TenantAccessTokenService
# =========================================================================

class TestTenantAccessTokenService:
    @pytest.fixture
    def service(self):
        from frontegg.common.clients.token_resolvers.access_token_services.services.tenant_access_token_service import (
            TenantAccessTokenService,
        )
        http = _mock_http_client()
        return TenantAccessTokenService(http), http

    def test_should_handle_tenant_access_token(self, service):
        svc, _ = service
        assert svc.should_handle(TokenTypes.TenantAccessToken.value) is True
        assert svc.should_handle(TokenTypes.UserAccessToken.value) is False

    def test_get_entity_from_identity_calls_correct_endpoint(self, service):
        svc, http = service
        http.get.return_value = _make_response(
            {"roles": ["admin"], "permissions": ["write"]}
        )
        entity = {"sub": "tok-t1", "tenantId": "t"}
        result = svc.get_entity_from_identity(entity)

        url_called = http.get.call_args[0][0]
        assert "tenants/access-tokens/v1/" in url_called
        assert result["roles"] == ["admin"]

    def test_get_active_token_ids_calls_correct_endpoint(self, service):
        svc, http = service
        http.get.return_value = _make_response(["tid-1", "tid-2"])
        result = svc.get_active_access_token_ids_from_identity()

        url_called = http.get.call_args[0][0]
        assert "tenants/access-tokens/v1/active" in url_called
        assert result == ["tid-1", "tid-2"]

    def test_api_tokens_disabled_raises_unauthenticated(self, service):
        svc, http = service
        _, exc = _make_403_api_tokens_disabled()
        http.get.side_effect = exc

        with pytest.raises(UnauthenticatedException):
            svc.get_entity({"sub": "tok-t"})
