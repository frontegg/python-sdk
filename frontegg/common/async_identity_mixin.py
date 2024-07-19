import asyncio

import jwt
import os
from jwt import InvalidTokenError
from typing import Optional

from frontegg.common.frontegg_async_authenticator import FronteggAsyncAuthenticator
from frontegg.common.clients.token_resolvers.async_access_token_resolver import AccessTokenAsyncResolver
from frontegg.common.clients.token_resolvers.async_authorization_token_resolver import AuthorizationJWTAsyncResolver
from frontegg.helpers.frontegg_urls import frontegg_urls
from frontegg.helpers.logger import logger
from frontegg.helpers.retry import retry
from frontegg.common.clients.types import AuthHeaderType, IValidateTokenOptions
from frontegg.helpers.exceptions import UnauthenticatedException

jwt_decode_retry = os.environ.get('FRONTEGG_JWT_DECODE_RETRY') or '1'
jwt_decode_retry = int(jwt_decode_retry)
jwt_decode_retry_delay = os.environ.get('FRONTEGG_JWT_DECODE_RETRY_DELAY_MS') or '0'
jwt_decode_retry_delay = float(jwt_decode_retry_delay) / 1000


class IdentityAsyncClientMixin:
    __publicKey = os.environ['FRONTEGG_PUBLIC_KEY']

    __tokenResolvers = []
    def __init__(self, async_authenticator: FronteggAsyncAuthenticator):
        self.__async_authenticator = async_authenticator
        self.__tokenResolvers = [AuthorizationJWTAsyncResolver(), AccessTokenAsyncResolver(async_authenticator)]

    def get_public_key(self) -> str:
        return self.__publicKey

    async def validate_identity_on_token(
            self,
            token,
            options: Optional[IValidateTokenOptions] = None,
            type=AuthHeaderType.JWT.value
    ):
        logger.debug(f'verifying {options}, token: {token}')
        
        if type == AuthHeaderType.JWT.value:
            try:
                token = token.replace("Bearer ", "")
            except:
                logger.error("Failed to extract token - ", token)

        public_key = self.get_public_key()

        resolver = None
        for _resolver in self.__tokenResolvers:
            if _resolver.should_handle(type) is True:
                resolver = _resolver
                break
        if not resolver:
            logger.error("Failed to find token resolver")
            raise UnauthenticatedException()

        entity = await resolver.validate_token(token, public_key, options)
        return entity

    async def decode_jwt(self, authorization_header, verify: Optional[bool] = True):
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

    @retry(action='decode jwt', total_tries=jwt_decode_retry, retry_delay=jwt_decode_retry_delay)
    def __get_jwt_data(self, jwt_token, verify, public_key):
        if verify:
            return jwt.decode(jwt_token, public_key, algorithms=['RS256'], options={"verify_aud": False})
        return jwt.decode(jwt_token, algorithms=['RS256'], options={"verify_aud": False, "verify_signature": verify})
