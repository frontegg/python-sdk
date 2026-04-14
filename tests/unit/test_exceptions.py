"""Unit tests for the ``frontegg.helpers.exceptions`` hierarchy."""
from frontegg.helpers.exceptions import (
    HttpException,
    UnauthenticatedException,
    UnauthorizedException,
)


class TestExceptions:
    def test_http_exception_stores_fields(self):
        exc = HttpException("boom", 500, headers={"X-Foo": "1"})
        assert exc.content == "boom"
        assert exc.status_code == 500
        assert exc.headers == {"X-Foo": "1"}

    def test_unauthenticated_defaults(self):
        exc = UnauthenticatedException()
        assert exc.status_code == 401
        assert exc.content == "Unauthenticated"

    def test_unauthorized_defaults(self):
        exc = UnauthorizedException()
        assert exc.status_code == 403
        assert exc.content == "Unauthorized"

    def test_inheritance(self):
        assert isinstance(UnauthenticatedException(), HttpException)
        assert isinstance(UnauthorizedException(), HttpException)
