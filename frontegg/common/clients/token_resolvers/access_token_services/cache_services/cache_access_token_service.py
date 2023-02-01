import abc
from typing import List, TypeVar, Union
from frontegg.common.clients.types import IAccessToken, IEntityWithRoles, TokenTypes, IEmptyAccessToken
from frontegg.common.cache.cache_manager import CacheManager
from frontegg.helpers.exceptions import UnauthenticatedException
from frontegg.common.clients.token_resolvers.access_token_services.base_access_token_service import \
    BaseAccessTokenService

T = TypeVar('T', bound=IAccessToken)


class CacheAccessTokenService(abc.ABC, BaseAccessTokenService[T]):
    def __init__(
            self,
            entity_cache_manager: CacheManager[Union[IEntityWithRoles, IEmptyAccessToken]],
            active_access_tokens_cache_manager: CacheManager[List[str]],
            access_token_service: BaseAccessTokenService[T],
            type: Union[TokenTypes.UserAccessToken.value, TokenTypes.TenantAccessToken.value]
    ):
        self.entity_cache_manager = entity_cache_manager
        self.active_access_tokens_cache_manager = active_access_tokens_cache_manager
        self.access_token_service = access_token_service
        self.type = type

    def get_entity(self, entity: T) -> IEntityWithRoles:
        cache_key = self.get_cache_prefix() + '_' + entity.get('sub')
        cached_data = self.entity_cache_manager.get(cache_key)

        if cached_data is not None:
            if self.__is_empty_access_token(cached_data):
                raise UnauthenticatedException()

            return cached_data

        try:
            data = self.access_token_service.get_entity(entity)
            self.entity_cache_manager.set(cache_key, data, {'expires_in_seconds': 10})

            return data
        except UnauthenticatedException:
            self.entity_cache_manager.set(cache_key, {'empty': True}, {'expires_in_seconds': 10})

    def get_active_access_token_ids(self) -> List[str]:
        cache_key = self.get_cache_prefix() + '_ids'
        cached_data = self.active_access_tokens_cache_manager.get(cache_key)

        if cached_data:
            return cached_data

        try:
            data = self.access_token_service.get_active_access_token_ids()
            self.active_access_tokens_cache_manager.set(cache_key, data, {'expires_in_seconds': 10})

            return data
        except UnauthenticatedException:
            self.active_access_tokens_cache_manager.set(cache_key, [], {'expires_in_seconds': 10})

    def __is_empty_access_token(self, access_token) -> bool:
        return 'empty' in access_token and access_token['empty'] is True
    @abc.abstractmethod
    def get_cache_prefix(self, access_token) -> str:
        pass
