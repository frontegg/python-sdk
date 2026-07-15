"""Unit tests for ``TokenResolver`` / ``AuthorizationJWTResolver``.

These tests use a real RSA keypair and PyJWT so signature verification is
actually exercised — no ``jwt.decode`` mocking.
"""
import jwt
import pytest

from frontegg.common.clients.token_resolvers.authorization_header_resolver import (
    AuthorizationJWTResolver,
)
from frontegg.common.clients.types import AuthHeaderType, TokenTypes
from frontegg.helpers.exceptions import (
    UnauthenticatedException,
    UnauthorizedException,
)


@pytest.fixture
def resolver():
    return AuthorizationJWTResolver()


class TestAuthorizationJWTResolver:
    def test_should_handle_jwt_type(self, resolver):
        assert resolver.should_handle(AuthHeaderType.JWT.value) is True
        assert resolver.should_handle(AuthHeaderType.AccessToken.value) is False

    def test_validates_user_token(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.UserToken.value})
        entity = resolver.validate_token(token, public_key)
        assert entity["sub"] == "user-123"
        assert entity["tenantId"] == "tenant-abc"

    def test_validates_user_api_token(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.UserApiToken.value})
        entity = resolver.validate_token(token, public_key)
        assert entity["type"] == TokenTypes.UserApiToken.value

    def test_rejects_disallowed_token_type(self, resolver, make_jwt, public_key):
        token = make_jwt({"type": TokenTypes.UserAccessToken.value})
        # UserAccessToken is not in the allowed types of the JWT resolver
        with pytest.raises(Exception):
            resolver.validate_token(token, public_key)

    def test_invalid_signature_raises_unauthenticated(
        self, resolver, make_jwt, public_key
    ):
        # Sign with a different key
        other_key = jwt.utils.force_bytes  # sentinel; we'll generate a new key
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        bad = rsa.generate_private_key(65537, 2048)
        bad_pem = bad.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        token = jwt.encode({"sub": "x", "type": "userToken"}, bad_pem, algorithm="RS256")

        with pytest.raises(UnauthenticatedException):
            resolver.validate_token(token, public_key)

    def test_malformed_token_raises_unauthenticated(self, resolver, public_key):
        with pytest.raises(UnauthenticatedException):
            resolver.validate_token("not-a-jwt", public_key)

    def test_role_check_passes_with_matching_role(
        self, resolver, make_jwt, public_key
    ):
        token = make_jwt({"roles": ["admin", "reader"]})
        entity = resolver.validate_token(
            token, public_key, options={"roles": ["admin"]}
        )
        assert entity["roles"] == ["admin", "reader"]

    def test_role_check_fails_when_no_overlap(
        self, resolver, make_jwt, public_key
    ):
        token = make_jwt({"roles": ["reader"]})
        with pytest.raises(UnauthorizedException):
            resolver.validate_token(
                token, public_key, options={"roles": ["admin"]}
            )

    def test_permission_check_passes(self, resolver, make_jwt, public_key):
        token = make_jwt({"permissions": ["fe.read", "fe.write"]})
        resolver.validate_token(
            token, public_key, options={"permissions": ["fe.write"]}
        )

    def test_permission_check_fails(self, resolver, make_jwt, public_key):
        token = make_jwt({"permissions": ["fe.read"]})
        with pytest.raises(UnauthorizedException):
            resolver.validate_token(
                token, public_key, options={"permissions": ["fe.admin"]}
            )

    def test_empty_options_does_not_check(self, resolver, make_jwt, public_key):
        token = make_jwt({"roles": [], "permissions": []})
        entity = resolver.validate_token(
            token, public_key, options={"roles": [], "permissions": []}
        )
        assert entity["sub"] == "user-123"

    def test_get_entity_is_identity(self, resolver):
        entity = {"sub": "abc", "roles": [], "permissions": []}
        assert resolver.get_entity(entity) is entity


class TestValidateRolesAndPermissions:
    """Exercise the static helper directly for boundary cases."""

    def test_no_options_is_noop(self):
        from frontegg.common.clients.token_resolvers.token_resolver import TokenResolver

        TokenResolver.validate_roles_and_permissions(
            {"roles": [], "permissions": []}, None
        )

    def test_at_least_one_role_suffices(self):
        from frontegg.common.clients.token_resolvers.token_resolver import TokenResolver

        TokenResolver.validate_roles_and_permissions(
            {"roles": ["a"], "permissions": []}, {"roles": ["a", "b"]}
        )

    def test_insufficient_roles_raises_unauthorized(self):
        from frontegg.common.clients.token_resolvers.token_resolver import TokenResolver

        with pytest.raises(UnauthorizedException):
            TokenResolver.validate_roles_and_permissions(
                {"roles": ["other"], "permissions": []}, {"roles": ["a"]}
            )
