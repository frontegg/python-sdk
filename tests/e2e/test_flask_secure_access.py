"""End-to-end tests for Flask ``@with_authentication``.

Builds a real Flask app, wires the ``frontegg`` singleton with a fake vendor
session + real RSA keys, and exercises protected endpoints through the
Flask test client — the same path a real request would travel.
"""
import pytest
from flask import Flask, g, jsonify

from frontegg.flask import frontegg
from frontegg.flask.secure_access import with_authentication


@pytest.fixture
def app(fake_vendor_session, reset_flask_frontegg):
    app = Flask("e2e")
    reset_flask_frontegg.init_app("client-id", "api-key")

    @app.route("/public")
    def public():
        return jsonify({"ok": True})

    @app.route("/me")
    @with_authentication()
    def me():
        return jsonify({"sub": g.user["sub"], "tenantId": g.user["tenantId"]})

    @app.route("/admin-only")
    @with_authentication(role_keys=["admin"])
    def admin_only():
        return jsonify({"ok": True})

    @app.route("/needs-write")
    @with_authentication(permission_keys=["fe.write"])
    def needs_write():
        return jsonify({"ok": True})

    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestFlaskSecureAccess:
    def test_public_route_unchanged(self, client):
        r = client.get("/public")
        assert r.status_code == 200
        assert r.get_json() == {"ok": True}

    def test_missing_auth_header_returns_401(self, client):
        r = client.get("/me")
        assert r.status_code == 401

    def test_invalid_jwt_returns_401(self, client):
        r = client.get("/me", headers={"Authorization": "Bearer garbage"})
        assert r.status_code == 401

    def test_valid_jwt_returns_entity(self, client, valid_jwt):
        r = client.get("/me", headers={"Authorization": "Bearer " + valid_jwt})
        assert r.status_code == 200
        assert r.get_json() == {"sub": "user-123", "tenantId": "tenant-abc"}

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
