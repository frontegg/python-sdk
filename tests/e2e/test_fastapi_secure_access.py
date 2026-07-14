"""End-to-end tests for FastAPI ``FronteggSecurity`` dependency.

Builds a real FastAPI app wired to the async ``frontegg`` singleton with
fake vendor session + real RSA keys. Exercises protected endpoints via
FastAPI's ``TestClient`` (which runs the async handlers synchronously).
"""
import asyncio

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from frontegg.fastapi import frontegg
from frontegg.fastapi.secure_access import FronteggSecurity, User


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def fastapi_app(fake_async_vendor_session, reset_fastapi_frontegg):
    _run(reset_fastapi_frontegg.init_app("client-id", "api-key"))

    app = FastAPI()

    @app.get("/public")
    def public():
        return {"ok": True}

    @app.get("/me")
    def me(user: User = Depends(FronteggSecurity())):
        return {"sub": user.sub, "tenant": user.tenant_id}

    @app.get("/admin-only")
    def admin_only(user: User = Depends(FronteggSecurity(roles=["admin"]))):
        return {"ok": True}

    @app.get("/needs-write")
    def needs_write(
        user: User = Depends(FronteggSecurity(permissions=["fe.write"]))
    ):
        return {"ok": True}

    return app


@pytest.fixture
def client(fastapi_app):
    return TestClient(fastapi_app)


class TestFastAPISecureAccess:
    def test_public_route(self, client):
        assert client.get("/public").json() == {"ok": True}

    def test_missing_auth_returns_401(self, client):
        assert client.get("/me").status_code == 401

    def test_invalid_jwt_returns_401(self, client):
        r = client.get("/me", headers={"Authorization": "Bearer garbage"})
        assert r.status_code == 401

    def test_valid_jwt_returns_user(self, client, valid_jwt):
        r = client.get(
            "/me", headers={"Authorization": "Bearer " + valid_jwt}
        )
        assert r.status_code == 200
        assert r.json() == {"sub": "user-123", "tenant": "tenant-abc"}

    def test_role_guard_allows_admin(self, client, valid_jwt):
        r = client.get(
            "/admin-only", headers={"Authorization": "Bearer " + valid_jwt}
        )
        assert r.status_code == 200

    def test_role_guard_rejects_non_admin(self, client, make_jwt):
        token = make_jwt({"roles": ["reader"]})
        r = client.get(
            "/admin-only", headers={"Authorization": "Bearer " + token}
        )
        assert r.status_code == 403

    def test_permission_guard_rejects_missing_perm(self, client, make_jwt):
        token = make_jwt({"permissions": ["fe.read"]})
        r = client.get(
            "/needs-write", headers={"Authorization": "Bearer " + token}
        )
        assert r.status_code == 403

    def test_permission_guard_allows_with_perm(self, client, make_jwt):
        token = make_jwt({"permissions": ["fe.write"]})
        r = client.get(
            "/needs-write", headers={"Authorization": "Bearer " + token}
        )
        assert r.status_code == 200
