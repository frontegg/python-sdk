"""Unit tests for the FastAPI-side ``Frontegg`` wrapper (async)."""
import asyncio


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestFastAPIFronteggWrapper:
    def test_init_app_creates_async_authenticator(
        self, fake_async_vendor_session, reset_fastapi_frontegg
    ):
        run(reset_fastapi_frontegg.init_app("client", "secret"))
        assert reset_fastapi_frontegg.async_authenticator is not None
        assert reset_fastapi_frontegg.async_identity_client is not None
        assert reset_fastapi_frontegg.access_token == "fake-vendor-token"

    def test_validate_identity_on_token_async(
        self, fake_async_vendor_session, reset_fastapi_frontegg, valid_jwt
    ):
        run(reset_fastapi_frontegg.init_app("c", "s"))
        entity = run(
            reset_fastapi_frontegg.validate_identity_on_token(
                "Bearer " + valid_jwt, None, "JWT"
            )
        )
        assert entity["sub"] == "user-123"

    def test_decode_jwt_async(
        self, fake_async_vendor_session, reset_fastapi_frontegg, valid_jwt
    ):
        run(reset_fastapi_frontegg.init_app("c", "s"))
        decoded = run(reset_fastapi_frontegg.decode_jwt("Bearer " + valid_jwt))
        assert decoded["tenantId"] == "tenant-abc"
