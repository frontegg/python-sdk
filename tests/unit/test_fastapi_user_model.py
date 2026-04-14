"""Unit tests for the FastAPI ``User`` Pydantic model and ``get_auth_header``."""
from unittest.mock import MagicMock

from frontegg.fastapi.secure_access.frontegg_security import (
    TokenType,
    User,
    get_auth_header,
)


def _user(**overrides):
    base = {
        "sub": "user-123",
        "tenantId": "tenant-abc",
        "applicationId": "app-xyz",
        "type": "userToken",
        "roles": ["admin"],
        "permissions": ["fe.read"],
        "access_token": "t",
    }
    base.update(overrides)
    return User(**base)


class TestUserModel:
    def test_builds_from_minimal_claims(self):
        u = _user()
        assert u.sub == "user-123"
        assert u.tenant_id == "tenant-abc"
        assert u.token_type == TokenType.UserToken

    def test_has_permissions_all_required(self):
        u = _user(permissions=["a", "b"])
        assert u.has_permissions(["a"]) is True
        assert u.has_permissions(["a", "b"]) is True
        assert u.has_permissions(["a", "c"]) is False
        assert u.has_permissions([]) is False  # empty list ⇒ False

    def test_has_roles_all_required(self):
        u = _user(roles=["admin", "ops"])
        assert u.has_roles(["admin"]) is True
        assert u.has_roles(["admin", "ops"]) is True
        assert u.has_roles(["admin", "missing"]) is False

    def test_id_for_user_token_returns_sub(self):
        u = _user(type="userToken")
        assert u.id == "user-123"

    def test_id_for_user_api_token_prefers_created_by(self):
        u = _user(type="userApiToken", createdByUserId="creator-9")
        assert u.id == "creator-9"

    def test_id_for_tenant_api_token_is_none(self):
        u = _user(type="tenantApiToken")
        assert u.id is None


class TestGetAuthHeader:
    def _req(self, headers):
        req = MagicMock()
        req.headers = headers
        return req

    def test_bearer_returns_jwt(self):
        assert get_auth_header(
            self._req({"Authorization": "Bearer xyz"})
        ) == {"token": "xyz", "type": "JWT"}

    def test_x_api_key_returns_access_token(self):
        assert get_auth_header(
            self._req({"x-api-key": "k"})
        ) == {"token": "k", "type": "AccessToken"}

    def test_no_auth_headers_returns_none(self):
        assert get_auth_header(self._req({})) is None
