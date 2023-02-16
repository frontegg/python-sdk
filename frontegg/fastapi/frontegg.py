from typing import Optional
from frontegg.common import FronteggAuthenticator, IdentityClientMixin
from frontegg.common.frontegg_context import FronteggContext


class Frontegg:
    def __init__(self):
        self.authenticator: FronteggAuthenticator = None
        self.identity_client: IdentityClientMixin = None

    def init_app(self, client_id: str, api_key: str, options={}):
        FronteggContext.init(options)
        self.authenticator = FronteggAuthenticator(client_id, api_key)
        self.identity_client = IdentityClientMixin(self.authenticator)

    @property
    def should_refresh_vendor_token(self) -> bool:
        return self.authenticator.should_refresh_vendor_token

    @property
    def access_token(self):
        return self.authenticator.access_token

    def refresh_vendor_token(self) -> None:
        self.authenticator.refresh_vendor_token()

    @property
    def client_id(self):
        return frontegg.authenticator.client_id

    @property
    def api_key(self):
        return frontegg.authenticator.api_key

    def get_public_key(self) -> str:
        return self.identity_client.get_public_key()

    def fetch_public_key(self) -> str:
        return self.identity_client.fetch_public_key()

    def validate_identity_on_token(
            self,
            token,
            options,
            type,
    ):
        return self.identity_client.validate_identity_on_token(token, options, type)

    def decode_jwt(self, authorization_header, verify: Optional[bool] = True):
        return self.identity_client.decode_jwt(authorization_header, verify)


frontegg = Frontegg()
