"""Unit tests for ``frontegg.helpers.retry.retry`` decorator."""
import pytest

from frontegg.helpers.retry import retry


class TestRetry:
    def test_returns_value_on_first_success(self):
        @retry(action="test", total_tries=3)
        def f():
            return 42

        assert f() == 42

    def test_retries_then_succeeds(self):
        calls = {"n": 0}

        @retry(action="test", total_tries=3, retry_delay=0)
        def flaky():
            calls["n"] += 1
            if calls["n"] < 2:
                raise ValueError("nope")
            return "ok"

        assert flaky() == "ok"
        assert calls["n"] == 2

    def test_raises_after_exhausting_retries(self):
        calls = {"n": 0}

        @retry(action="test", total_tries=3, retry_delay=0)
        def always_fails():
            calls["n"] += 1
            raise RuntimeError("bad")

        with pytest.raises(RuntimeError, match="bad"):
            always_fails()
        assert calls["n"] == 3

    def test_preserves_function_name(self):
        @retry(action="test", total_tries=1)
        def my_function():
            return None

        assert my_function.__name__ == "my_function"
