"""Unit tests for the Flask-side ``Frontegg`` wrapper."""
import pytest

from frontegg.flask import frontegg as fe_flask_singleton


class TestFlaskFronteggWrapper:
    def test_init_app_creates_authenticator_and_identity(
        self, fake_vendor_session, reset_flask_frontegg
    ):
        reset_flask_frontegg.init_app("client", "secret")
        assert reset_flask_frontegg.authenticator is not None
        assert reset_flask_frontegg.identity_client is not None
        assert reset_flask_frontegg.access_token == "fake-vendor-token"

    def test_validate_identity_on_token(
        self, fake_vendor_session, reset_flask_frontegg, valid_jwt
    ):
        reset_flask_frontegg.init_app("c", "s")
        entity = reset_flask_frontegg.validate_identity_on_token(
            "Bearer " + valid_jwt, None, "JWT"
        )
        assert entity["sub"] == "user-123"

    def test_decode_jwt_roundtrip(
        self, fake_vendor_session, reset_flask_frontegg, valid_jwt
    ):
        reset_flask_frontegg.init_app("c", "s")
        decoded = reset_flask_frontegg.decode_jwt("Bearer " + valid_jwt)
        assert decoded["tenantId"] == "tenant-abc"
