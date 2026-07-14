"""Unit tests for ``IdentityAsyncClientMixin``.

Mirrors the sync identity_mixin tests but exercises the async path:
public key fetch, caching, token validation, and JWT decode.
"""
import asyncio

import jwt
import pytest

from frontegg.common import FronteggAsyncAuthenticator, IdentityAsyncClientMixin
from frontegg.common.clients.types import AuthHeaderType, TokenTypes
from frontegg.helpers.exceptions import UnauthenticatedException


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def identity(fake_async_vendor_session):
    auth = FronteggAsyncAuthenticator("c", "s")
    _run(auth.refresh_vendor_token())
    return IdentityAsyncClientMixin(auth)


class TestAsyncFetchPublicKey:
    def test_fetches_public_key(self, identity, public_key):
        key = _run(identity.fetch_public_key())
        assert key == public_key

    def test_caches_public_key(self, identity, fake_async_vendor_session):
        _run(identity.get_public_key())
        _run(identity.get_public_key())
        _run(identity.get_public_key())
        # Only one GET call
        assert len(fake_async_vendor_session.get_calls) == 1


class TestAsyncValidateIdentityOnToken:
    def test_valid_jwt_returns_entity(self, identity, valid_jwt):
        entity = _run(
            identity.validate_identity_on_token(
                "Bearer " + valid_jwt, None, AuthHeaderType.JWT.value
            )
        )
        assert entity["sub"] == "user-123"
        assert entity["tenantId"] == "tenant-abc"

    def test_strips_bearer_prefix(self, identity, valid_jwt):
        a = _run(
            identity.validate_identity_on_token(
                "Bearer " + valid_jwt, None, AuthHeaderType.JWT.value
            )
        )
        b = _run(
            identity.validate_identity_on_token(
                valid_jwt, None, AuthHeaderType.JWT.value
            )
        )
        assert a == b

    def test_invalid_token_raises_unauthenticated(self, identity):
        with pytest.raises(UnauthenticatedException):
            _run(
                identity.validate_identity_on_token(
                    "Bearer garbage", None, AuthHeaderType.JWT.value
                )
            )

    def test_unknown_resolver_type_raises(self, identity, valid_jwt):
        with pytest.raises(UnauthenticatedException):
            _run(
                identity.validate_identity_on_token(
                    valid_jwt, None, "NOPE"
                )
            )

    def test_role_enforcement(self, identity, make_jwt):
        from frontegg.helpers.exceptions import UnauthorizedException

        token = make_jwt({"roles": ["reader"]})
        with pytest.raises(UnauthorizedException):
            _run(
                identity.validate_identity_on_token(
                    "Bearer " + token,
                    {"roles": ["admin"], "permissions": None},
                    AuthHeaderType.JWT.value,
                )
            )


class TestAsyncDecodeJwt:
    def test_missing_header_raises(self, identity):
        with pytest.raises(jwt.InvalidTokenError):
            _run(identity.decode_jwt(None))

    def test_decodes_valid_jwt(self, identity, valid_jwt):
        decoded = _run(identity.decode_jwt("Bearer " + valid_jwt))
        assert decoded["sub"] == "user-123"

    def test_decode_without_verification(self, identity, make_jwt):
        token = make_jwt()
        decoded = _run(identity.decode_jwt("Bearer " + token, verify=False))
        assert decoded["sub"] == "user-123"
