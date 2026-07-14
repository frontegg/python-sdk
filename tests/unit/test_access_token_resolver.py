"""Unit tests for ``AccessTokenResolver`` — mirrors nodejs-sdk access-token-resolver.spec.ts.

Covers:
- shouldHandle routing (AccessToken yes, JWT no)
- RS256 JWT verification against public key
- Active token ID validation (rejects revoked tokens)
- Service routing based on token type (User vs Tenant)
- Role/permission fetching via get_entity when options require it
- UnauthenticatedException when no service matches token type
- Token not in active IDs → UnauthenticatedException
"""
from unittest.mock import MagicMock, patch

import pytest

from frontegg.common.clients.types import AuthHeaderType, TokenTypes
from frontegg.helpers.exceptions import UnauthenticatedException, UnauthorizedException


@pytest.fixture
def resolver(fake_vendor_session):
    """Build an ``AccessTokenResolver`` with mocked access token services."""
    from frontegg.common import FronteggAuthenticator
    from frontegg.common.clients.token_resolvers.access_token_resolver import AccessTokenResolver

    auth = FronteggAuthenticator("c", "s")
    resolver = AccessTokenResolver(auth)
    return resolver


def _make_mock_service(token_type, entity_data=None, active_ids=None):
    svc = MagicMock()
    svc.should_handle = lambda t: t == token_type
    svc.get_entity.return_value = entity_data or {}
    svc.get_active_access_token_ids.return_value = active_ids or []
    return svc


class TestAccessTokenResolverShouldHandle:
    def test_handles_access_token(self, resolver):
        assert resolver.should_handle(AuthHeaderType.AccessToken.value) is True

    def test_does_not_handle_jwt(self, resolver):
        assert resolver.should_handle(AuthHeaderType.JWT.value) is False


class TestAccessTokenResolverValidateToken:
    def test_valid_token_active_id_passes(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.UserAccessToken.value, "sub": "tok-123"})
        svc = _make_mock_service(
            TokenTypes.UserAccessToken.value, active_ids=["tok-123"]
        )
        resolver._AccessTokenResolver__access_token_services = [svc]

        entity = resolver.validate_token(token, public_key)
        assert entity["sub"] == "tok-123"
        svc.get_active_access_token_ids.assert_called_once()

    def test_token_not_in_active_ids_raises(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.UserAccessToken.value, "sub": "tok-123"})
        svc = _make_mock_service(
            TokenTypes.UserAccessToken.value, active_ids=["other-tok"]
        )
        resolver._AccessTokenResolver__access_token_services = [svc]

        with pytest.raises(UnauthenticatedException):
            resolver.validate_token(token, public_key)

    def test_fetches_entity_roles_when_roles_required(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.TenantAccessToken.value, "sub": "tok-456"})
        entity_with_roles = {
            "sub": "tok-456",
            "tenantId": "t",
            "type": TokenTypes.TenantAccessToken.value,
            "roles": ["admin"],
            "permissions": ["read"],
        }
        svc = _make_mock_service(
            TokenTypes.TenantAccessToken.value,
            entity_data=entity_with_roles,
            active_ids=["tok-456"],
        )
        resolver._AccessTokenResolver__access_token_services = [svc]

        result = resolver.validate_token(
            token, public_key, options={"roles": ["admin"], "permissions": None}
        )
        svc.get_entity.assert_called_once()
        assert result["roles"] == ["admin"]

    def test_fetches_entity_when_permissions_required(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.UserAccessToken.value, "sub": "tok-789"})
        entity_with_roles = {
            "sub": "tok-789",
            "roles": [],
            "permissions": ["write"],
        }
        svc = _make_mock_service(
            TokenTypes.UserAccessToken.value,
            entity_data=entity_with_roles,
        )
        resolver._AccessTokenResolver__access_token_services = [svc]

        result = resolver.validate_token(
            token, public_key, options={"permissions": ["write"], "roles": None}
        )
        svc.get_entity.assert_called_once()

    def test_insufficient_role_raises_unauthorized(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.TenantAccessToken.value, "sub": "tok-x"})
        entity_with_roles = {
            "sub": "tok-x",
            "roles": ["viewer"],
            "permissions": [],
        }
        svc = _make_mock_service(
            TokenTypes.TenantAccessToken.value,
            entity_data=entity_with_roles,
        )
        resolver._AccessTokenResolver__access_token_services = [svc]

        with pytest.raises(UnauthorizedException):
            resolver.validate_token(
                token, public_key, options={"roles": ["admin"], "permissions": None}
            )

    def test_routes_to_correct_service_by_token_type(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.TenantAccessToken.value, "sub": "tok-t"})

        tenant_svc = _make_mock_service(
            TokenTypes.TenantAccessToken.value, active_ids=["tok-t"]
        )
        user_svc = _make_mock_service(
            TokenTypes.UserAccessToken.value, active_ids=[]
        )
        resolver._AccessTokenResolver__access_token_services = [user_svc, tenant_svc]

        resolver.validate_token(token, public_key)
        tenant_svc.get_active_access_token_ids.assert_called_once()
        user_svc.get_active_access_token_ids.assert_not_called()

    def test_no_matching_service_raises(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.TenantAccessToken.value, "sub": "tok-t"})
        no_match = MagicMock()
        no_match.should_handle = lambda t: False
        resolver._AccessTokenResolver__access_token_services = [no_match]

        with pytest.raises(UnauthenticatedException):
            resolver.validate_token(token, public_key)

    def test_invalid_signature_raises(self, resolver, public_key):
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import jwt

        bad_key = rsa.generate_private_key(65537, 2048)
        bad_pem = bad_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        token = jwt.encode(
            {"sub": "x", "type": TokenTypes.UserAccessToken.value},
            bad_pem,
            algorithm="RS256",
        )
        with pytest.raises(UnauthenticatedException):
            resolver.validate_token(token, public_key)
