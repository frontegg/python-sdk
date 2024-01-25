from typing import Optional

from frontegg.common import FronteggAsyncAuthenticator, IdentityAsyncClientMixin
from frontegg.common.frontegg_context import FronteggContext


class Frontegg:
    def __init__(self):
        self.async_authenticator: FronteggAsyncAuthenticator = None
        self.async_identity_client: IdentityAsyncClientMixin = None

    async def init_app(self, client_id: str, api_key: str, options={}):
        FronteggContext.init(options)
        self.async_authenticator = FronteggAsyncAuthenticator(client_id, api_key)
        await self.async_authenticator.refresh_vendor_token()
        self.async_identity_client = IdentityAsyncClientMixin(self.async_authenticator)

    @property
    def should_refresh_vendor_token(self) -> bool:
        return self.async_authenticator.should_refresh_vendor_token

    @property
    def access_token(self):
        return self.async_authenticator.access_token

    async def refresh_vendor_token(self) -> None:
        await self.async_authenticator.refresh_vendor_token()

    @property
    def client_id(self):
        return frontegg.async_authenticator.client_id

    @property
    def api_key(self):
        return frontegg.async_authenticator.api_key

    async def get_public_key(self) -> str:
        return await self.async_identity_client.get_public_key()

    async def fetch_public_key(self) -> str:
        return await self.async_identity_client.fetch_public_key()

    async def validate_identity_on_token(
            self,
            token,
            options,
            type,
    ):
        return await self.async_identity_client.validate_identity_on_token(token, options, type)

    async def decode_jwt(self, authorization_header, verify: Optional[bool] = True):
        return await self.async_identity_client.decode_jwt(authorization_header, verify)


frontegg = Frontegg()
