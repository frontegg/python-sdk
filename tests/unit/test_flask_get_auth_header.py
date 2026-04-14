"""Unit tests for Flask ``get_auth_header`` helper."""
from flask import Flask

from frontegg.flask.secure_access.with_authentication import get_auth_header


def _ctx(headers):
    app = Flask(__name__)
    return app.test_request_context("/", headers=headers)


class TestGetAuthHeader:
    def test_extracts_bearer_as_jwt(self):
        with _ctx({"Authorization": "Bearer abc.def.ghi"}):
            from flask import request

            assert get_auth_header(request) == {"token": "abc.def.ghi", "type": "JWT"}

    def test_extracts_x_api_key_as_access_token(self):
        with _ctx({"x-api-key": "secret-access-token"}):
            from flask import request

            assert get_auth_header(request) == {
                "token": "secret-access-token",
                "type": "AccessToken",
            }

    def test_none_when_no_headers(self):
        with _ctx({}):
            from flask import request

            assert get_auth_header(request) is None

    def test_authorization_preferred_over_api_key(self):
        with _ctx({"Authorization": "Bearer jwt-t", "x-api-key": "at-t"}):
            from flask import request

            result = get_auth_header(request)
            assert result["type"] == "JWT"
            assert result["token"] == "jwt-t"
