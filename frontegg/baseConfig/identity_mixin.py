from abc import ABCMeta, abstractmethod
from frontegg.helpers.frontegg_urls import frontegg_urls
import typing
import jwt
import requests
from frontegg.helpers.logger import logger
from jwt import InvalidTokenError
from frontegg.helpers.retry import retry
import os

jwt_decode_retry = os.environ.get('FRONTEGG_JWT_DECODE_RETRY') or '1'
jwt_decode_retry = int(jwt_decode_retry)

class IdentityClientMixin(metaclass=ABCMeta):
    __publicKey = None

    @property
    @abstractmethod
    def vendor_session_request(self) -> requests.Session:
        pass

    @property
    @abstractmethod
    def should_refresh_vendor_token(self) -> bool:
        pass

    @abstractmethod
    def refresh_vendor_token(self) -> None:
        pass

    def get_public_key(self) -> str:
        if self.__publicKey:
            return self.__publicKey

        logger.info('could not find public key locally, will fetch public key')
        reties = 0
        while reties < 10:
            try:
                self.__publicKey = self.fetch_public_key()
                return self.__publicKey
            except Exception as e:
                reties = reties + 1
                logger.error(
                    'could not get public key from frontegg, retry number - ' + str(reties) + ', ' + str(e))

        logger.error('failed to get public key in all retries')

    def fetch_public_key(self) -> str:

        if self.should_refresh_vendor_token:
            self.refresh_vendor_token()

        response = self.vendor_session_request.get(
            frontegg_urls.identity_service['vendor_config'])
        response.raise_for_status()
        data = response.json()
        return data.get('publicKey')


    def decode_jwt(self, authorization_header, verify: typing.Optional[bool] = True):
        if not authorization_header:
            raise InvalidTokenError('Authorization headers is missing')
        logger.debug('found authorization header: ' +
                     str(authorization_header))
        jwt_token = authorization_header.replace('Bearer ', '')
        public_key = self.get_public_key()
        logger.debug('got public key' + str(public_key))
        decoded = self.__get_jwt_data(jwt_token, verify, public_key)
        logger.info('jwt was decoded successfully')
        logger.debug('JWT value - ' + str(decoded))
        return decoded


    @retry(action='decode jwt', total_tries=jwt_decode_retry)
    def __get_jwt_data(self, jwt_token, verify, public_key):
        if verify:
            return jwt.decode(jwt_token, public_key, algorithms='RS256', options={"verify_aud": False})
        return jwt.decode(jwt_token, algorithms='RS256', verify=verify, options={"verify_aud": False})
