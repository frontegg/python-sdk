"""Audit v2 contract tests through the SDK HTTP client and serializer."""
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlparse

import pytest
import requests

from frontegg.common.clients.audits_client import AuditsClient
from frontegg.common.clients.http_client import HttpClient


@pytest.fixture
def audits(fake_vendor_session):
    http = HttpClient("client", "secret", "https://example.test/audits/")
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"data": [{"frontegg_id": "audit-1"}], "total": 1}'
    http.client.send = MagicMock(return_value=response)
    return AuditsClient(http), http, response


def test_structured_filters_and_authentication(audits):
    client, http, _ = audits
    result = client.get_audits_v2(
        "tenant-1", 200, 0,
        created_from="2026-11-01T00:00:00Z",
        created_to="2026-11-19T00:00:00Z",
        tenant_ids=["tenant-1", "tenant-2"], users=["user-1", "user-2"],
        email=["a+b@example.test", "other@example.test"],
        sort_by="createdAt", sort_direction="desc",
        query_filter='{"action":"login"}', feature_flag_id="feature-1",
    )
    request = http.client.send.call_args.args[0]
    assert urlparse(request.url).path == "/audits/resources/audits/v2"
    assert parse_qs(urlparse(request.url).query) == {
        "count": ["200"], "offset": ["0"],
        "created_from": ["2026-11-01T00:00:00Z"],
        "created_to": ["2026-11-19T00:00:00Z"],
        "tenant_ids": ["tenant-1", "tenant-2"],
        "users": ["user-1", "user-2"],
        "email": ["a+b@example.test", "other@example.test"],
        "sortBy": ["createdAt"], "sortDirection": ["desc"],
        "filter": ['{"action":"login"}'], "featureFlagId": ["feature-1"],
    }
    assert request.headers["frontegg-tenant-id"] == "tenant-1"
    assert request.headers["x-access-token"] == "fake-vendor-token"
    assert result == {"data": [{"frontegg_id": "audit-1"}], "total": 1}
    http.client.send.assert_called_once()


def test_optional_filters_and_tenant_switch(audits):
    client, http, _ = audits
    for tenant in ("tenant-1", "tenant-2"):
        client.get_audits_v2(tenant, 1, 0)
        request = http.client.send.call_args.args[0]
        assert request.headers["frontegg-tenant-id"] == tenant
        assert parse_qs(urlparse(request.url).query) == {
            "count": ["1"], "offset": ["0"]
        }


@pytest.mark.parametrize("status", [400, 401, 404, 500])
def test_http_errors_propagate(audits, status):
    client, _, response = audits
    response.status_code = status
    with pytest.raises(requests.HTTPError):
        client.get_audits_v2("tenant-1", 1, 0)


def test_timeout_propagates(audits):
    client, http, _ = audits
    http.client.send.side_effect = requests.Timeout("timed out")
    with pytest.raises(requests.Timeout):
        client.get_audits_v2("tenant-1", 1, 0)


def test_invalid_json_propagates(audits):
    client, _, response = audits
    response._content = b'not json'
    with pytest.raises(requests.exceptions.JSONDecodeError):
        client.get_audits_v2("tenant-1", 1, 0)
