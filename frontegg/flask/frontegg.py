from frontegg.common import FronteggAuthenticator, IdentityClientMixin


class Frontegg(FronteggAuthenticator, IdentityClientMixin):
    def __init__(self):
        pass

    def init_app(self, client_id: str, api_key: str):
        super(Frontegg, self).__init__(client_id, api_key)


frontegg = Frontegg()
