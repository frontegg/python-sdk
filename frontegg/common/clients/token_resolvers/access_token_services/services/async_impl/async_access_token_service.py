import abc
import json
from typing import List, TypeVar, Union
from frontegg.common.clients.types import IAccessToken, IEntityWithRoles, TokenTypes
from frontegg.helpers.exceptions import UnauthenticatedException
from frontegg.helpers.logger import logger
from frontegg.common.clients.token_resolvers.access_token_services.base_access_token_service import \
    BaseAccessTokenService

T = TypeVar('T', bound=IAccessToken)


class AccessTokenAsyncService(abc.ABC, BaseAccessTokenService[T]):
    def __init__(self, type: Union[TokenTypes.UserAccessToken.value, TokenTypes.TenantAccessToken.value]):
        self.type = type

    async def get_entity(self, entity: T) -> IEntityWithRoles:
        try:
            data = await self.get_entity_from_identity(entity)
            return data
        except Exception as e:
            logger.exception('Failed to get entity from identity')
            if self.__is_api_tokens_disabled(e):
                raise UnauthenticatedException()

            raise e

    async def get_active_access_token_ids(self) -> List[str]:
        try:
            return await self.get_active_access_token_ids_from_identity()
        except Exception as e:
            logger.exception('Failed to get active access token ids')
            if self.__is_api_tokens_disabled(e):
                raise UnauthenticatedException()

            raise e

    @abc.abstractmethod
    async def get_entity_from_identity(self, entity: T) -> IEntityWithRoles:
        pass

    @abc.abstractmethod
    async def get_active_access_token_ids_from_identity(self) -> List[str]:
        pass

    def __is_api_tokens_disabled(self, error):
        try:
            return json.loads(error.response.text).get('errors')[0] == 'Api tokens are disabled' and error.response.status_code == 403
        except:
            return True


