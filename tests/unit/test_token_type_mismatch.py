"""Unit tests for token type mismatch detection — mirrors
nodejs-sdk identity-client.spec.ts "should throw if provided token in the
wrong header" tests.

The Python SDK should reject:
- A user JWT token presented via x-api-key (AccessToken header type)
- An access token presented via Authorization header (JWT header type)
"""
import pytest

from frontegg.common import FronteggAuthenticator, IdentityClientMixin
from frontegg.common.clients.types import AuthHeaderType, TokenTypes
from frontegg.helpers.exceptions import UnauthenticatedException


@pytest.fixture
def identity(fake_vendor_session):
    auth = FronteggAuthenticator("c", "s")
    return IdentityClientMixin(auth)


class TestTokenTypeMismatch:
    def test_user_token_in_access_token_header_raises(self, identity, make_jwt):
        """User JWT token sent via x-api-key should be rejected.

        The AccessToken resolver only allows UserAccessToken/TenantAccessToken
        types, so a userToken JWT will fail type validation.
        """
        token = make_jwt({"type": TokenTypes.UserToken.value})
        with pytest.raises(Exception):
            identity.validate_identity_on_token(
                token, None, AuthHeaderType.AccessToken.value
            )

    def test_tenant_api_token_in_access_token_header_raises(self, identity, make_jwt):
        """TenantApiToken sent via x-api-key should be rejected by the
        AccessToken resolver (wrong token type)."""
        token = make_jwt({"type": TokenTypes.TenantApiToken.value})
        with pytest.raises(Exception):
            identity.validate_identity_on_token(
                token, None, AuthHeaderType.AccessToken.value
            )

    def test_user_access_token_in_jwt_header_raises(self, identity, make_jwt):
        """UserAccessToken sent via Authorization header should be rejected
        by the JWT resolver (type not in allowed list)."""
        token = make_jwt({"type": TokenTypes.UserAccessToken.value})
        with pytest.raises(Exception):
            identity.validate_identity_on_token(
                "Bearer " + token, None, AuthHeaderType.JWT.value
            )

    def test_tenant_access_token_in_jwt_header_raises(self, identity, make_jwt):
        """TenantAccessToken sent via Authorization header should be rejected."""
        token = make_jwt({"type": TokenTypes.TenantAccessToken.value})
        with pytest.raises(Exception):
            identity.validate_identity_on_token(
                "Bearer " + token, None, AuthHeaderType.JWT.value
            )

    def test_unknown_header_type_raises(self, identity, make_jwt):
        """Completely unknown header type should raise UnauthenticatedException."""
        token = make_jwt()
        with pytest.raises(UnauthenticatedException):
            identity.validate_identity_on_token(token, None, "UNKNOWN_TYPE")

    def test_correct_user_token_in_jwt_header_passes(self, identity, make_jwt):
        """Sanity: userToken via Authorization header should work."""
        token = make_jwt({"type": TokenTypes.UserToken.value})
        entity = identity.validate_identity_on_token(
            "Bearer " + token, None, AuthHeaderType.JWT.value
        )
        assert entity["type"] == TokenTypes.UserToken.value

    def test_correct_user_api_token_in_jwt_header_passes(self, identity, make_jwt):
        token = make_jwt({"type": TokenTypes.UserApiToken.value})
        entity = identity.validate_identity_on_token(
            "Bearer " + token, None, AuthHeaderType.JWT.value
        )
        assert entity["type"] == TokenTypes.UserApiToken.value

    def test_correct_tenant_api_token_in_jwt_header_passes(self, identity, make_jwt):
        token = make_jwt({"type": TokenTypes.TenantApiToken.value})
        entity = identity.validate_identity_on_token(
            "Bearer " + token, None, AuthHeaderType.JWT.value
        )
        assert entity["type"] == TokenTypes.TenantApiToken.value
