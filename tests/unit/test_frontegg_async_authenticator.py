"""Unit tests for ``FronteggAsyncAuthenticator``."""
import asyncio

import pytest

from frontegg.common import FronteggAsyncAuthenticator


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestFronteggAsyncAuthenticator:
    def test_init_does_not_trigger_refresh(self, fake_async_vendor_session):
        # Unlike sync, async __init__ does NOT refresh (must be awaited).
        FronteggAsyncAuthenticator("client", "secret")
        assert fake_async_vendor_session.post_calls == []

    def test_refresh_populates_access_token(self, fake_async_vendor_session):
        auth = FronteggAsyncAuthenticator("client", "secret")
        assert auth.access_token is None
        run(auth.refresh_vendor_token())
        assert auth.access_token == "fake-vendor-token"
        assert len(fake_async_vendor_session.post_calls) == 1

    def test_refresh_sends_credentials_in_body(self, fake_async_vendor_session):
        auth = FronteggAsyncAuthenticator("c", "s")
        run(auth.refresh_vendor_token())
        assert fake_async_vendor_session.post_calls[0]["json"] == {
            "clientId": "c",
            "secret": "s",
        }

    def test_should_refresh_starts_true(self, fake_async_vendor_session):
        auth = FronteggAsyncAuthenticator("c", "s")
        assert auth.should_refresh_vendor_token is True
        run(auth.refresh_vendor_token())
        assert auth.should_refresh_vendor_token is False
