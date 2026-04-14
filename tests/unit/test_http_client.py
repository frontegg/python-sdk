"""Unit tests for ``HttpClient`` (Frontegg API HTTP wrapper)."""
from unittest.mock import MagicMock

import pytest

from frontegg.common.clients.http_client import HttpClient, prepare_headers


class TestPrepareHeaders:
    def test_merges_tenant_and_host(self):
        h = prepare_headers(tenant_id="t", host="h", headers={"X": "1"})
        assert h == {
            "frontegg-tenant-id": "t",
            "frontegg-vendor-host": "h",
            "X": "1",
        }

    def test_omits_missing_fields(self):
        h = prepare_headers(headers={"X": "1"})
        assert h == {"X": "1"}


@pytest.fixture
def http_client(fake_vendor_session):
    client = HttpClient("client", "secret", "https://api.frontegg.com/audits/")
    client.client = MagicMock(name="inner_session")
    client.client.get.return_value = MagicMock(status_code=200)
    client.client.post.return_value = MagicMock(status_code=201)
    client.client.put.return_value = MagicMock(status_code=200)
    client.client.delete.return_value = MagicMock(status_code=204)
    client.client.patch.return_value = MagicMock(status_code=200)
    client.client.headers = {}
    return client


class TestHttpClient:
    def test_get_sets_vendor_token_header(self, http_client):
        http_client.get("items", params={"q": "x"}, tenant_id="t")
        assert http_client.client.headers["x-access-token"] == "fake-vendor-token"
        http_client.client.get.assert_called_once()
        args, kwargs = http_client.client.get.call_args
        assert "items" in args[0]
        assert kwargs["params"] == {"q": "x"}
        assert kwargs["headers"]["frontegg-tenant-id"] == "t"

    def test_post_sends_json(self, http_client):
        http_client.post({"a": 1}, url="things")
        _, kwargs = http_client.client.post.call_args
        assert kwargs["json"] == {"a": 1}

    def test_put_delete_patch_fire_corresponding_methods(self, http_client):
        http_client.put({"a": 1}, url="t")
        http_client.delete(url="t")
        http_client.patch({"b": 2}, url="t")
        http_client.client.put.assert_called_once()
        http_client.client.delete.assert_called_once()
        http_client.client.patch.assert_called_once()
