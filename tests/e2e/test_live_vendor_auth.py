"""Live e2e tests against the real Frontegg API.

These tests hit the live Frontegg API — they validate that the SDK's
vendor authentication, public-key fetching, JWT validation, and
framework-level secure access actually work end-to-end with real HTTP.

Run with:
    FRONTEGG_TEST_CLIENT_ID=... FRONTEGG_TEST_API_KEY=... \
        pytest tests/e2e/test_live_vendor_auth.py -v

Skip when credentials are absent (CI without secrets, local dev, etc.).
"""
from __future__ import annotations

import asyncio
import os
import time

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

LIVE_CLIENT_ID = os.environ.get("FRONTEGG_TEST_CLIENT_ID")
LIVE_API_KEY = os.environ.get("FRONTEGG_TEST_API_KEY")

pytestmark = pytest.mark.skipif(
    not LIVE_CLIENT_ID or not LIVE_API_KEY,
    reason="FRONTEGG_TEST_CLIENT_ID / FRONTEGG_TEST_API_KEY not set",
)


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_live_public_key():
    """Fetch the real Frontegg public key via the SDK."""
    from frontegg.common import FronteggAuthenticator, IdentityClientMixin

    auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
    identity = IdentityClientMixin(auth)
    return identity.fetch_public_key()


def _make_fake_jwt(overrides=None):
    """Sign a JWT with a random RSA key (NOT Frontegg's) — always invalid."""
    key = rsa.generate_private_key(65537, 2048)
    priv = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    now = int(time.time())
    payload = {
        "sub": "fake-user",
        "tenantId": "fake-tenant",
        "applicationId": "fake-app",
        "type": "userToken",
        "roles": ["admin"],
        "permissions": ["fe.read"],
        "iat": now,
        "exp": now + 3600,
    }
    if overrides:
        payload.update(overrides)
    return jwt.encode(payload, priv, algorithm="RS256")


# ===========================================================================
# 1. VENDOR AUTHENTICATION
# ===========================================================================


class TestLiveSyncAuth:
    def test_vendor_token_is_returned(self):
        from frontegg.common import FronteggAuthenticator

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        assert auth.access_token is not None
        assert len(auth.access_token) > 100
        assert auth.should_refresh_vendor_token is False

    def test_refresh_updates_token(self):
        from frontegg.common import FronteggAuthenticator

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        auth.refresh_vendor_token()
        assert auth.access_token is not None
        assert auth.should_refresh_vendor_token is False

    def test_bad_credentials_raise(self):
        from frontegg.common import FronteggAuthenticator

        with pytest.raises(Exception):
            FronteggAuthenticator(LIVE_CLIENT_ID, "wrong-api-key")

    def test_bad_client_id_raises(self):
        from frontegg.common import FronteggAuthenticator

        with pytest.raises(Exception):
            FronteggAuthenticator("00000000-0000-0000-0000-000000000000", LIVE_API_KEY)


class TestLiveAsyncAuth:
    def _fresh_auth(self, client_id, api_key):
        from httpx import AsyncClient as AC
        from frontegg.common import FronteggAsyncAuthenticator

        auth = FronteggAsyncAuthenticator(client_id, api_key)
        auth.vendor_session_request = AC()  # fresh client per test
        return auth

    def test_vendor_token_is_returned(self):
        auth = self._fresh_auth(LIVE_CLIENT_ID, LIVE_API_KEY)
        assert auth.access_token is None
        _run(auth.refresh_vendor_token())
        assert auth.access_token is not None
        assert len(auth.access_token) > 100
        assert auth.should_refresh_vendor_token is False

    def test_bad_credentials_raise_async(self):
        auth = self._fresh_auth(LIVE_CLIENT_ID, "wrong-api-key")
        with pytest.raises(Exception):
            _run(auth.refresh_vendor_token())


# ===========================================================================
# 2. PUBLIC KEY FETCH
# ===========================================================================


class TestLivePublicKeySync:
    def test_fetch_public_key(self):
        from frontegg.common import FronteggAuthenticator, IdentityClientMixin

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        identity = IdentityClientMixin(auth)
        public_key = identity.fetch_public_key()
        assert public_key.startswith("-----BEGIN PUBLIC KEY-----")

    def test_get_public_key_caches(self):
        from frontegg.common import FronteggAuthenticator, IdentityClientMixin

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        identity = IdentityClientMixin(auth)
        k1 = identity.get_public_key()
        k2 = identity.get_public_key()
        assert k1 == k2

    def test_public_key_is_valid_rsa(self):
        pk_pem = _get_live_public_key()
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        key = load_pem_public_key(pk_pem.encode())
        assert key.key_size >= 2048


class TestLivePublicKeyAsync:
    def test_fetch_public_key_async(self):
        from httpx import AsyncClient as AC
        from frontegg.common import FronteggAsyncAuthenticator, IdentityAsyncClientMixin

        async def _test():
            auth = FronteggAsyncAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
            auth.vendor_session_request = AC()
            await auth.refresh_vendor_token()
            identity = IdentityAsyncClientMixin(auth)
            return await identity.fetch_public_key()

        public_key = _run(_test())
        assert public_key.startswith("-----BEGIN PUBLIC KEY-----")


# ===========================================================================
# 3. IDENTITY VALIDATION WITH LIVE PUBLIC KEY
# ===========================================================================


class TestLiveIdentityValidation:
    """Validate that the SDK correctly rejects forged tokens when using
    the real Frontegg public key."""

    def test_fake_jwt_rejected_by_live_public_key(self):
        from frontegg.common import FronteggAuthenticator, IdentityClientMixin
        from frontegg.helpers.exceptions import UnauthenticatedException

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        identity = IdentityClientMixin(auth)
        fake_token = _make_fake_jwt()

        with pytest.raises(UnauthenticatedException):
            identity.validate_identity_on_token(
                "Bearer " + fake_token, None, "JWT"
            )

    def test_expired_fake_jwt_rejected(self):
        from frontegg.common import FronteggAuthenticator, IdentityClientMixin
        from frontegg.helpers.exceptions import UnauthenticatedException

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        identity = IdentityClientMixin(auth)
        expired = _make_fake_jwt({"exp": int(time.time()) - 3600})

        with pytest.raises(UnauthenticatedException):
            identity.validate_identity_on_token(
                "Bearer " + expired, None, "JWT"
            )

    def test_garbage_token_rejected(self):
        from frontegg.common import FronteggAuthenticator, IdentityClientMixin
        from frontegg.helpers.exceptions import UnauthenticatedException

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        identity = IdentityClientMixin(auth)

        with pytest.raises(UnauthenticatedException):
            identity.validate_identity_on_token(
                "Bearer not.a.real.jwt.at.all", None, "JWT"
            )

    def test_empty_bearer_rejected(self):
        from frontegg.common import FronteggAuthenticator, IdentityClientMixin
        from frontegg.helpers.exceptions import UnauthenticatedException

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        identity = IdentityClientMixin(auth)

        with pytest.raises(UnauthenticatedException):
            identity.validate_identity_on_token("Bearer ", None, "JWT")

    def test_decode_jwt_rejects_missing_header(self):
        from frontegg.common import FronteggAuthenticator, IdentityClientMixin

        auth = FronteggAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
        identity = IdentityClientMixin(auth)

        with pytest.raises(Exception):
            identity.decode_jwt(None)


# ===========================================================================
# 4. FLASK E2E WITH LIVE VENDOR TOKEN + REJECTION OF FORGED JWTs
# ===========================================================================


class TestLiveFlaskSecureAccess:
    @pytest.fixture
    def flask_client(self):
        from flask import Flask, g, jsonify
        from frontegg.flask.frontegg import Frontegg
        from frontegg.flask.secure_access import with_authentication

        fe = Frontegg()
        fe.init_app(LIVE_CLIENT_ID, LIVE_API_KEY)
        app = Flask("live-flask-e2e")

        @app.route("/public")
        def public():
            return jsonify({"ok": True})

        @app.route("/protected")
        @with_authentication()
        def protected():
            return jsonify({"sub": g.user["sub"]})

        @app.route("/admin-only")
        @with_authentication(role_keys=["admin"])
        def admin_only():
            return jsonify({"ok": True})

        # Monkey-patch the module-level frontegg used by with_authentication
        import frontegg.flask as flask_mod
        old = flask_mod.frontegg
        flask_mod.frontegg = fe
        yield app.test_client()
        flask_mod.frontegg = old

    def test_public_endpoint_works(self, flask_client):
        assert flask_client.get("/public").status_code == 200

    def test_no_header_returns_401(self, flask_client):
        assert flask_client.get("/protected").status_code == 401

    def test_forged_jwt_returns_401(self, flask_client):
        token = _make_fake_jwt()
        r = flask_client.get(
            "/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert r.status_code == 401

    def test_garbage_token_returns_401(self, flask_client):
        r = flask_client.get(
            "/protected",
            headers={"Authorization": "Bearer xyz.abc.def"},
        )
        assert r.status_code == 401

    def test_forged_admin_token_returns_401(self, flask_client):
        token = _make_fake_jwt({"roles": ["admin"]})
        r = flask_client.get(
            "/admin-only", headers={"Authorization": f"Bearer {token}"}
        )
        assert r.status_code == 401  # signature mismatch, not 403


# ===========================================================================
# 5. FASTAPI E2E WITH LIVE VENDOR TOKEN + REJECTION OF FORGED JWTs
# ===========================================================================


class TestLiveFastAPISecureAccess:
    @pytest.fixture
    def fastapi_client(self):
        from httpx import AsyncClient as AC
        from fastapi import Depends, FastAPI
        from fastapi.testclient import TestClient
        from frontegg.fastapi.frontegg import Frontegg
        from frontegg.fastapi.secure_access import FronteggSecurity, User

        fe = Frontegg()
        fe.async_authenticator = None
        fe.async_identity_client = None

        async def _init():
            from frontegg.common import FronteggAsyncAuthenticator, IdentityAsyncClientMixin
            from frontegg.common.frontegg_context import FronteggContext
            FronteggContext.init({})
            auth = FronteggAsyncAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
            auth.vendor_session_request = AC()
            await auth.refresh_vendor_token()
            fe.async_authenticator = auth
            fe.async_identity_client = IdentityAsyncClientMixin(auth)

        _run(_init())
        app = FastAPI()

        @app.get("/public")
        def public():
            return {"ok": True}

        @app.get("/protected")
        def protected(user: User = Depends(FronteggSecurity())):
            return {"sub": user.sub}

        @app.get("/admin-only")
        def admin_only(user: User = Depends(FronteggSecurity(roles=["admin"]))):
            return {"ok": True}

        import frontegg.fastapi as fastapi_mod
        old = fastapi_mod.frontegg
        fastapi_mod.frontegg = fe
        yield TestClient(app)
        fastapi_mod.frontegg = old

    def test_public_endpoint_works(self, fastapi_client):
        assert fastapi_client.get("/public").status_code == 200

    def test_no_header_returns_401(self, fastapi_client):
        assert fastapi_client.get("/protected").status_code == 401

    def test_forged_jwt_returns_401(self, fastapi_client):
        token = _make_fake_jwt()
        r = fastapi_client.get(
            "/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert r.status_code == 401

    def test_garbage_token_returns_401(self, fastapi_client):
        r = fastapi_client.get(
            "/protected",
            headers={"Authorization": "Bearer xyz.abc.def"},
        )
        assert r.status_code == 401

    def test_forged_admin_token_returns_401(self, fastapi_client):
        token = _make_fake_jwt({"roles": ["admin"]})
        r = fastapi_client.get(
            "/admin-only", headers={"Authorization": f"Bearer {token}"}
        )
        assert r.status_code == 401


# ===========================================================================
# 6. SDK WRAPPER INIT
# ===========================================================================


class TestLiveFlaskSDKInit:
    def test_init_app_and_get_public_key(self):
        from frontegg.flask.frontegg import Frontegg

        fe = Frontegg()
        fe.init_app(LIVE_CLIENT_ID, LIVE_API_KEY)
        assert fe.access_token is not None
        pk = fe.get_public_key()
        assert pk.startswith("-----BEGIN PUBLIC KEY-----")


class TestLiveFastAPISDKInit:
    def test_init_app_and_get_public_key(self):
        from httpx import AsyncClient as AC
        from frontegg.common import FronteggAsyncAuthenticator, IdentityAsyncClientMixin
        from frontegg.common.frontegg_context import FronteggContext
        from frontegg.fastapi.frontegg import Frontegg

        fe = Frontegg()

        async def _init():
            FronteggContext.init({})
            auth = FronteggAsyncAuthenticator(LIVE_CLIENT_ID, LIVE_API_KEY)
            auth.vendor_session_request = AC()
            await auth.refresh_vendor_token()
            fe.async_authenticator = auth
            fe.async_identity_client = IdentityAsyncClientMixin(auth)

        _run(_init())
        assert fe.access_token is not None
        pk = _run(fe.get_public_key())
        assert pk.startswith("-----BEGIN PUBLIC KEY-----")


# ===========================================================================
# 7. HTTP CLIENT
# ===========================================================================


class TestLiveHttpClient:
    def test_get_vendor_config(self):
        from frontegg.common.clients.http_client import HttpClient

        client = HttpClient(
            LIVE_CLIENT_ID,
            LIVE_API_KEY,
            "https://api.frontegg.com/identity/",
        )
        resp = client.get("resources/configurations/v1/")
        assert resp.status_code == 200
        assert "publicKey" in resp.json()

    def test_get_with_invalid_endpoint_returns_404(self):
        from frontegg.common.clients.http_client import HttpClient

        client = HttpClient(
            LIVE_CLIENT_ID,
            LIVE_API_KEY,
            "https://api.frontegg.com/identity/",
        )
        resp = client.get("resources/does-not-exist/")
        assert resp.status_code in (404, 403)

    def test_post_audits_endpoint(self):
        from frontegg.common.clients.http_client import HttpClient

        client = HttpClient(
            LIVE_CLIENT_ID,
            LIVE_API_KEY,
            "https://api.frontegg.com/audits/",
        )
        resp = client.post(
            {"severity": "Info", "action": "sdk-e2e-test"},
            tenant_id="test-tenant-id",
        )
        # Audit post may succeed or fail depending on tenant config,
        # but it must not crash the SDK.
        assert resp.status_code in (200, 201, 202, 400, 403, 404)


class TestLiveAsyncHttpClient:
    def test_get_vendor_config_async(self):
        from httpx import AsyncClient as AC
        from frontegg.common.clients.async_http_client import HttpAsyncClient

        client = HttpAsyncClient(
            LIVE_CLIENT_ID,
            LIVE_API_KEY,
            "https://api.frontegg.com/identity/",
        )
        client.vendor_session_request = AC()
        client.client = AC()

        async def _test():
            await client.refresh_vendor_token()
            return await client.get("resources/configurations/v1/")

        resp = _run(_test())
        assert resp.status_code == 200
        assert "publicKey" in resp.json()
