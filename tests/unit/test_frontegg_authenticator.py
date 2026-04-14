"""Unit tests for ``FronteggAuthenticator`` (sync vendor token refresh)."""
import arrow
import pytest

from frontegg.common import FronteggAuthenticator


class TestFronteggAuthenticator:
    def test_init_triggers_refresh(self, fake_vendor_session):
        FronteggAuthenticator("client", "secret")
        assert fake_vendor_session.post.call_count == 1
        # Request body carries clientId/secret
        _, kwargs = fake_vendor_session.post.call_args
        assert kwargs["json"] == {"clientId": "client", "secret": "secret"}

    def test_access_token_populated_after_init(self, fake_vendor_session):
        auth = FronteggAuthenticator("client", "secret")
        assert auth.access_token == "fake-vendor-token"

    def test_should_refresh_false_right_after_refresh(self, fake_vendor_session):
        auth = FronteggAuthenticator("client", "secret")
        assert auth.should_refresh_vendor_token is False

    def test_should_refresh_true_when_expired(self, fake_vendor_session, monkeypatch):
        auth = FronteggAuthenticator("client", "secret")
        # Force "now" to be 2h in the future — past the 1h vendor token.
        future = arrow.utcnow().shift(hours=2)
        monkeypatch.setattr("frontegg.common.frontegg_authenticator.arrow.utcnow", lambda: future)
        assert auth.should_refresh_vendor_token is True

    def test_refresh_is_idempotent(self, fake_vendor_session):
        auth = FronteggAuthenticator("client", "secret")
        auth.refresh_vendor_token()
        assert fake_vendor_session.post.call_count == 2
        assert auth.access_token == "fake-vendor-token"

    def test_http_error_propagates(self, fake_vendor_session):
        from tests.conftest import _FakeResponse

        fake_vendor_session.post.return_value = _FakeResponse({}, status_code=500)
        with pytest.raises(RuntimeError, match="HTTP 500"):
            FronteggAuthenticator("client", "secret")
