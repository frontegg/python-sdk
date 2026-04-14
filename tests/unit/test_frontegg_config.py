"""Unit tests for ``frontegg.common.FronteggConfig``."""
import pytest

from frontegg.common import FronteggConfig


class TestFronteggConfig:
    def test_stores_credentials(self):
        cfg = FronteggConfig("client-id", "api-key")
        assert cfg.client_id == "client-id"
        assert cfg.api_key == "api-key"

    def test_rejects_missing_client_id(self):
        with pytest.raises(Exception, match="client_id is required"):
            FronteggConfig(None, "api-key")

    def test_rejects_missing_api_key(self):
        with pytest.raises(Exception, match="api_key is required"):
            FronteggConfig("client-id", None)
