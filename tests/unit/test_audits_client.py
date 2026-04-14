"""Unit tests for ``AuditsClient``."""
from unittest.mock import MagicMock

import pytest

from frontegg.common.clients.audits_client import AuditsClient, Severity


class TestSeverityEnum:
    def test_values(self):
        assert Severity.INFO.value == "Info"
        assert Severity.CRITICAL.value == "Critical"
        assert Severity.ERROR.value == "Error"


class TestAuditsClient:
    def test_send_audit_posts_and_returns_json(self):
        http = MagicMock()
        response = MagicMock()
        response.json.return_value = {"id": "aud-1", "severity": "Info"}
        http.post.return_value = response

        client = AuditsClient(http)
        result = client.send_audit(
            {"severity": "Info", "username": "u"}, tenant_id="tenant-1"
        )

        http.post.assert_called_once_with(
            data={"severity": "Info", "username": "u"}, tenant_id="tenant-1"
        )
        assert result == {"id": "aud-1", "severity": "Info"}

    def test_send_audit_raises_on_http_error(self):
        http = MagicMock()
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        http.post.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            AuditsClient(http).send_audit({"severity": "Info"}, tenant_id="t")
