from httpx import AsyncClient
import arrow
import os

from frontegg.common.frontegg_config import FronteggConfig
from frontegg.helpers.frontegg_urls import frontegg_urls
from frontegg.helpers.logger import logger


class FronteggAsyncAuthenticator(FronteggConfig):
    __access_token = None
    __refresh_token = None
    __access_token_expiration = None
    vendor_session_request = AsyncClient()

    def __init__(self, client_id: str, api_key: str):
        super(FronteggAsyncAuthenticator, self).__init__(client_id, api_key)

    @property
    def access_token(self):
        return self.__access_token

    @property
    def should_refresh_token(self) -> bool:
        return self.__access_token is None \
            or self.__access_token_expiration is None \
            or arrow.utcnow() >= self.__access_token_expiration

    async def init(self):
        body = {
            "clientId": os.environ['FRONTEGG_CLIENT_ID'],
            "secret": os.environ['FRONTEGG_SECRET']
        }

        logger.info('Will get access and refresh tokens')
        auth_url = frontegg_urls.authentication_service['authenticate']

        auth_response = await self.vendor_session_request.post(auth_url, json=body, timeout=3)
        auth_response.raise_for_status()
        logger.info('Got new access and refresh tokens from frontegg')
        response_body = auth_response.json()
        self.__access_token = response_body['access_token']
        self.__refresh_token = response_body['refresh_token']
        self.__access_token_expiration = calcTokenExpiration(response_body['expires_in'])
        self.vendor_session_request.headers.update({'x-access-token': self.__access_token})
        logger.info('New access token was set successfully')


    async def refresh_token(self) -> None:
        body = {
            'refreshToken': self.__refresh_token,
        }
        
        logger.info('Will refresh access token')
        auth_url = frontegg_urls.authentication_service['refresh_token']

        auth_response = await self.vendor_session_request.post(auth_url, json=body, timeout=3)
        auth_response.raise_for_status()
        logger.info('Got a new vendor token from frontegg')
        response_body = auth_response.json()
        self.__access_token = response_body['access_token']
        self.__refresh_token = response_body['refresh_token']
        self.__access_token_expiration = calcTokenExpiration(response_body['expiresIn'])
        self.vendor_session_request.headers.update({'x-access-token': self.__access_token})
        logger.info('New access token was set successfully')


def calcTokenExpiration(expiration):
    return arrow.utcnow().shift(seconds=expiration * 0.8)
