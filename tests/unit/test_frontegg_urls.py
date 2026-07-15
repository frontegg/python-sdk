"""Unit tests for ``frontegg.helpers.frontegg_urls.FronteggUrls``."""
import importlib


def _reload_urls(monkeypatch, env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    module = importlib.import_module("frontegg.helpers.frontegg_urls")
    return importlib.reload(module)


class TestFronteggUrls:
    def test_default_base_url(self):
        from frontegg.helpers.frontegg_urls import FronteggUrls

        urls = FronteggUrls()
        assert urls.base_url.endswith("/")
        assert "api.frontegg.com" in urls.base_url

    def test_authenticate_vendor_endpoint(self):
        from frontegg.helpers.frontegg_urls import FronteggUrls

        urls = FronteggUrls()
        vendor = urls.authentication_service["authenticate_vendor"]
        assert vendor.endswith("/auth/vendor/")

    def test_identity_vendor_config_endpoint(self):
        from frontegg.helpers.frontegg_urls import FronteggUrls

        urls = FronteggUrls()
        cfg = urls.identity_service["vendor_config"]
        assert cfg.endswith("/identity/resources/configurations/v1/")

    def test_gateway_env_override(self, monkeypatch):
        mod = _reload_urls(
            monkeypatch, {"FRONTEGG_API_GATEWAY_URL": "https://eu.frontegg.com"}
        )
        urls = mod.FronteggUrls()
        assert urls.base_url == "https://eu.frontegg.com/"
        assert urls.authentication_service["authenticate_vendor"].startswith(
            "https://eu.frontegg.com/auth/"
        )
