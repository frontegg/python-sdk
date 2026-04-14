"""Unit tests for ``frontegg.common.package_utils.PackageUtils``."""
import pytest

from frontegg.common.package_utils import PackageUtils


class TestPackageUtils:
    def test_loads_existing_package(self):
        mod = PackageUtils.load_package("json")
        assert mod.__name__ == "json"

    def test_missing_package_raises_with_name(self):
        with pytest.raises(Exception, match="definitely_not_a_real_package_xyz"):
            PackageUtils.load_package("definitely_not_a_real_package_xyz")
