import jwt
import abc
import os
from typing import List, Optional, Union, TypeVar, Generic
from frontegg.common.clients.types import IEntity, IEntityWithRoles, IValidateTokenOptions, TokenTypes
from frontegg.helpers.logger import logger
from frontegg.helpers.retry import retry
from frontegg.helpers.exceptions import UnauthorizedException, UnauthenticatedException

T = TypeVar('T', bound=IEntity)

jwt_decode_retry = os.environ.get('FRONTEGG_JWT_DECODE_RETRY') or '1'
jwt_decode_retry = int(jwt_decode_retry)
jwt_decode_retry_delay = os.environ.get('FRONTEGG_JWT_DECODE_RETRY_DELAY_MS') or '0'
jwt_decode_retry_delay = float(jwt_decode_retry_delay) / 1000


class TokenResolver(Generic[T], abc.ABC):
    def __init__(self, allowed_token_types: List[TokenTypes], type: str):
        self.allowed_token_types = allowed_token_types
        self.type = type

    @abc.abstractmethod
    def validate_token(self, token: str, public_key: str, options: Optional[IValidateTokenOptions] = None) -> Union[IEntity, IEntityWithRoles]:
        pass

    def verify_token(self, token: str, public_key: str) -> IEntity:
        entity = self.verify_async(token, public_key)
        self.validate_token_type(entity.get('type'))
        return entity

    def validate_token_type(self, token_type: TokenTypes):
        if token_type not in self.allowed_token_types:
            logger.info('Invalid token type')
            raise Exception()

    @staticmethod
    def validate_roles_and_permissions(entity: IEntityWithRoles, options: Optional[IValidateTokenOptions] = None):
        if options is not None:
            roles = options.get('roles')
            permissions = options.get('permissions')
            if roles is not None and len(roles) > 0:
                have_at_least_one_role = False
                for requested_role in roles:
                    if requested_role in entity.get('roles'):
                        have_at_least_one_role = True
                        break
                if not have_at_least_one_role:
                    logger.info('Insufficient role')
                    raise UnauthorizedException()

            if permissions is not None and len(permissions) > 0:
                have_at_least_one_permission = False
                for requested_permission in permissions:
                    if requested_permission in entity.get('permissions'):
                        have_at_least_one_permission = True
                        break
                if not have_at_least_one_permission:
                    logger.info('Insufficient permission')
                    raise UnauthorizedException()

    @abc.abstractmethod
    def get_entity(self, entity: IEntity) -> IEntityWithRoles:
        pass

    def should_handle(self, type: str) -> bool:
        return self.type == type

    def verify_async(self, token: str, public_key: str) -> IEntity:
        try:
            decoded = self.__get_jwt_data(token, public_key)
            return decoded
        except jwt.exceptions.DecodeError as e:
            logger.info('Failed to verify jwt - {}'.format(e))
            raise UnauthenticatedException()

    @retry(action='decode jwt', total_tries=jwt_decode_retry, retry_delay=jwt_decode_retry_delay)
    def __get_jwt_data(self, token: str, public_key: str, verify: Optional[bool] = True):
        if verify:
            return jwt.decode(token, public_key, algorithms=['RS256'], options={"verify_aud": False})
        return jwt.decode(token, algorithms=['RS256'], options={"verify_aud": False, "verify_signature": verify})
