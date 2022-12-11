from frontegg.common.frontegg_config import FronteggConfig
import requests
from frontegg.helpers.frontegg_urls import frontegg_urls
import arrow
from frontegg.helpers.logger import logger


class FronteggAuthenticator(FronteggConfig):
    __access_token = None
    __access_token_expiration = None
    vendor_session_request = requests.session()

    def __init__(self, client_id: str, api_key: str):
        super(FronteggAuthenticator, self).__init__(client_id, api_key)
        self.refresh_vendor_token()

    @property
    def access_token(self):
        return self.__access_token

    @property
    def should_refresh_vendor_token(self) -> bool:
        return self.__access_token is None \
               or self.__access_token_expiration is None \
               or arrow.utcnow() >= self.__access_token_expiration

    def refresh_vendor_token(self) -> None:
        body = {
            'clientId': self.client_id,
            'secret': self.api_key
        }
        logger.info('Will refresh vendor token')
        auth_url = frontegg_urls.authentication_service['authenticate_vendor']

        auth_response = self.vendor_session_request.post(auth_url, json=body)
        auth_response.raise_for_status()
        logger.info('Got a new vendor token from frontegg')
        response_body = auth_response.json()
        self.__access_token = response_body['token']
        self.__access_token_expiration = calcTokenExpiration(response_body['expiresIn'])
        self.vendor_session_request.headers.update({'x-access-token': self.__access_token})
        logger.info('New vendor token was set successfully')


def calcTokenExpiration(expiration): return arrow.utcnow().shift(seconds=expiration * 0.8)
