"""Shared test fixtures for the Frontegg Python SDK test suite.

Provides:
- An RSA keypair + helpers to mint RS256 JWTs (so tests exercise real signature
  verification instead of mocking out PyJWT).
- Fakes for the vendor-token refresh HTTP call so instantiating
  ``FronteggAuthenticator``/``FronteggAsyncAuthenticator`` never hits the network.
- Singleton resetters for ``FronteggContext`` and the Flask/FastAPI ``frontegg``
  modules so tests stay isolated.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Iterator, Optional
from unittest.mock import MagicMock

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


# ---------------------------------------------------------------------------
# RSA keypair / JWT helpers
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def rsa_keypair():
    """Generate an RSA keypair once per session; return (private_pem, public_pem)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


@pytest.fixture
def private_key(rsa_keypair) -> str:
    return rsa_keypair[0]


@pytest.fixture
def public_key(rsa_keypair) -> str:
    return rsa_keypair[1]


def _default_payload() -> Dict[str, Any]:
    now = int(time.time())
    return {
        "sub": "user-123",
        "tenantId": "tenant-abc",
        "applicationId": "app-xyz",
        "type": "userToken",
        "roles": ["admin"],
        "permissions": ["fe.read"],
        "email": "user@example.com",
        "name": "Test User",
        "iat": now,
        "exp": now + 3600,
    }


@pytest.fixture
def make_jwt(private_key):
    """Return a factory that signs a JWT with the session RSA key."""

    def _make(overrides: Optional[Dict[str, Any]] = None, algorithm: str = "RS256") -> str:
        payload = _default_payload()
        if overrides:
            payload.update(overrides)
        return jwt.encode(payload, private_key, algorithm=algorithm)

    return _make


@pytest.fixture
def valid_jwt(make_jwt) -> str:
    return make_jwt()


# ---------------------------------------------------------------------------
# Vendor token / public key mocking
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, json_data: Any, status_code: int = 200):
        self._json = json_data
        self.status_code = status_code
        self.headers: Dict[str, str] = {}

    def json(self) -> Any:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.fixture
def fake_vendor_session(public_key) -> Iterator[MagicMock]:
    """Patch ``FronteggAuthenticator.vendor_session_request`` so no real HTTP fires.

    The patched session:
    - Responds to POST (vendor auth) with a fake token + 1h expiry.
    - Responds to GET (public key fetch) with the session public key.
    """
    from frontegg.common import frontegg_authenticator as mod

    mock_session = MagicMock(name="vendor_session_request")
    mock_session.post.return_value = _FakeResponse(
        {"token": "fake-vendor-token", "expiresIn": 3600}
    )
    mock_session.get.return_value = _FakeResponse({"publicKey": public_key})
    mock_session.headers = {}

    original = mod.FronteggAuthenticator.vendor_session_request
    mod.FronteggAuthenticator.vendor_session_request = mock_session
    try:
        yield mock_session
    finally:
        mod.FronteggAuthenticator.vendor_session_request = original


@pytest.fixture
def fake_async_vendor_session(public_key):
    """Async equivalent: patch ``FronteggAsyncAuthenticator.vendor_session_request``."""
    from frontegg.common import frontegg_async_authenticator as mod

    class _AsyncFake:
        def __init__(self):
            self.headers: Dict[str, str] = {}
            self.post_calls = []
            self.get_calls = []

        async def post(self, url, json=None, timeout=None):
            self.post_calls.append({"url": url, "json": json})
            return _FakeResponse({"token": "fake-vendor-token", "expiresIn": 3600})

        async def get(self, url, timeout=None):
            self.get_calls.append({"url": url})
            return _FakeResponse({"publicKey": public_key})

    fake = _AsyncFake()
    original = mod.FronteggAsyncAuthenticator.vendor_session_request
    mod.FronteggAsyncAuthenticator.vendor_session_request = fake
    try:
        yield fake
    finally:
        mod.FronteggAsyncAuthenticator.vendor_session_request = original


# ---------------------------------------------------------------------------
# Singleton resetters
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_frontegg_context():
    """``FronteggContext`` is a process-wide singleton; wipe it between tests."""
    from frontegg.common.frontegg_context import FronteggContext

    FronteggContext._instance = None
    FronteggContext.options = {}
    yield
    FronteggContext._instance = None
    FronteggContext.options = {}


@pytest.fixture
def reset_flask_frontegg():
    """Reset the module-level Flask ``frontegg`` singleton."""
    import frontegg.flask as fe_flask

    saved_auth = fe_flask.frontegg.authenticator
    saved_id = fe_flask.frontegg.identity_client
    fe_flask.frontegg.authenticator = None
    fe_flask.frontegg.identity_client = None
    yield fe_flask.frontegg
    fe_flask.frontegg.authenticator = saved_auth
    fe_flask.frontegg.identity_client = saved_id


@pytest.fixture
def reset_fastapi_frontegg():
    import frontegg.fastapi as fe_fastapi

    saved_auth = fe_fastapi.frontegg.async_authenticator
    saved_id = fe_fastapi.frontegg.async_identity_client
    fe_fastapi.frontegg.async_authenticator = None
    fe_fastapi.frontegg.async_identity_client = None
    yield fe_fastapi.frontegg
    fe_fastapi.frontegg.async_authenticator = saved_auth
    fe_fastapi.frontegg.async_identity_client = saved_id
