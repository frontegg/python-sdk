from typing import Optional

from frontegg.common.frontegg_async_authenticator import FronteggAsyncAuthenticator
from frontegg.common.async_identity_mixin import IdentityAsyncClientMixin
from frontegg.common.frontegg_context import FronteggContext


class Frontegg:
    def __init__(self):
        self.async_authenticator: FronteggAsyncAuthenticator = None
        self.async_identity_client: IdentityAsyncClientMixin = None

    async def init_app(self, client_id: str, api_key: str, options={}):
        FronteggContext.init(options)
        self.async_authenticator = FronteggAsyncAuthenticator(client_id, api_key)
        await self.async_authenticator.init()

        self.async_identity_client = IdentityAsyncClientMixin(self.async_authenticator)

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
