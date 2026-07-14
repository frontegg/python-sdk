from frontegg.common.clients.types import AuthHeaderType
from frontegg.flask.secure_access.with_authentication import get_auth_header


class _FakeRequest:
    """Minimal stand-in for a Flask request exposing a ``headers`` mapping."""

    def __init__(self, headers):
        self.headers = headers


def test_get_auth_header_reads_bearer_token():
    header = get_auth_header(_FakeRequest({'Authorization': 'Bearer my.jwt.token'}))

    assert header == {'token': 'my.jwt.token', 'type': AuthHeaderType.JWT.value}


def test_get_auth_header_reads_api_key():
    header = get_auth_header(_FakeRequest({'x-api-key': 'secret-key'}))

    assert header == {'token': 'secret-key', 'type': AuthHeaderType.AccessToken.value}


def test_get_auth_header_prefers_authorization_over_api_key():
    header = get_auth_header(
        _FakeRequest({'Authorization': 'Bearer jwt', 'x-api-key': 'secret-key'})
    )

    assert header == {'token': 'jwt', 'type': AuthHeaderType.JWT.value}


def test_get_auth_header_missing_returns_none():
    assert get_auth_header(_FakeRequest({})) is None


def test_with_authentication_rejects_request_without_auth_header(client):
    res = client.get('/protected')

    assert res.status_code == 401
