"""Unit tests for ``IdentityClientMixin``.

These test the full token-validation path: fetching the public key, caching
it in-memory, picking the right resolver, and returning the decoded entity.
"""
import jwt
import pytest

from frontegg.common import FronteggAuthenticator, IdentityClientMixin
from frontegg.common.clients.types import AuthHeaderType, TokenTypes
from frontegg.helpers.exceptions import (
    UnauthenticatedException,
    UnauthorizedException,
)


@pytest.fixture
def identity(fake_vendor_session):
    auth = FronteggAuthenticator("client", "secret")
    return IdentityClientMixin(auth)


class TestFetchPublicKey:
    def test_fetches_via_vendor_session(self, identity, fake_vendor_session, public_key):
        key = identity.fetch_public_key()
        assert key == public_key
        fake_vendor_session.get.assert_called()

    def test_get_public_key_caches_result(self, identity, fake_vendor_session):
        identity.get_public_key()
        identity.get_public_key()
        identity.get_public_key()
        # Only one GET call — subsequent calls return cached key.
        assert fake_vendor_session.get.call_count == 1


class TestValidateIdentityOnToken:
    def test_valid_jwt_returns_entity(self, identity, valid_jwt):
        entity = identity.validate_identity_on_token(
            "Bearer " + valid_jwt, None, AuthHeaderType.JWT.value
        )
        assert entity["sub"] == "user-123"
        assert entity["tenantId"] == "tenant-abc"

    def test_strips_bearer_prefix(self, identity, valid_jwt):
        # With and without the 'Bearer ' prefix must behave identically.
        a = identity.validate_identity_on_token(
            "Bearer " + valid_jwt, None, AuthHeaderType.JWT.value
        )
        b = identity.validate_identity_on_token(
            valid_jwt, None, AuthHeaderType.JWT.value
        )
        assert a == b

    def test_invalid_token_raises_unauthenticated(self, identity):
        with pytest.raises(UnauthenticatedException):
            identity.validate_identity_on_token(
                "Bearer garbage.not.a.jwt", None, AuthHeaderType.JWT.value
            )

    def test_role_enforcement_raises_unauthorized(self, identity, make_jwt):
        token = make_jwt({"roles": ["reader"]})
        with pytest.raises(UnauthorizedException):
            identity.validate_identity_on_token(
                "Bearer " + token,
                {"roles": ["admin"], "permissions": None},
                AuthHeaderType.JWT.value,
            )

    def test_permission_enforcement_passes_with_match(self, identity, make_jwt):
        token = make_jwt({"permissions": ["fe.read", "fe.write"]})
        entity = identity.validate_identity_on_token(
            "Bearer " + token,
            {"roles": None, "permissions": ["fe.write"]},
            AuthHeaderType.JWT.value,
        )
        assert "fe.write" in entity["permissions"]

    def test_unknown_resolver_type_raises(self, identity, valid_jwt):
        with pytest.raises(UnauthenticatedException):
            identity.validate_identity_on_token(valid_jwt, None, "NopeType")


class TestDecodeJwt:
    def test_missing_authorization_header_raises(self, identity):
        with pytest.raises(jwt.InvalidTokenError):
            identity.decode_jwt(None)

    def test_decodes_with_bearer_prefix(self, identity, valid_jwt):
        decoded = identity.decode_jwt("Bearer " + valid_jwt)
        assert decoded["sub"] == "user-123"

    def test_decode_unsigned_when_verify_false(self, identity, make_jwt):
        token = make_jwt()
        decoded = identity.decode_jwt("Bearer " + token, verify=False)
        assert decoded["sub"] == "user-123"
