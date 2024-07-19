from typing import Optional, List

from frontegg.common.frontegg_async_authenticator import FronteggAsyncAuthenticator
from frontegg.common.cache.local_cache_manager import LocalCacheManager
from frontegg.common.cache.redis_cache_manager import RedisCacheManager
from frontegg.common.clients.async_http_client import HttpAsyncClient
from frontegg.common.clients.token_resolvers.access_token_services.cache_services.async_impl.async_cache_tenant_access_token_service import \
    CacheTenantAccessTokenAsyncService
from frontegg.common.clients.token_resolvers.access_token_services.cache_services.async_impl.async_cache_user_access_token_service import \
    CacheUserAccessTokenAsyncService
from frontegg.common.clients.token_resolvers.access_token_services.services.async_impl.async_tenant_access_token_service import \
    TenantAccessTokenAsyncService
from frontegg.common.clients.token_resolvers.access_token_services.services.async_impl.async_user_access_token_service import \
    UserAccessTokenAsyncService
from frontegg.common.clients.token_resolvers.token_resolver import TokenResolver
from frontegg.common.clients.types import TokenTypes, AuthHeaderType, IEntityWithRoles, IValidateTokenOptions
from frontegg.common.frontegg_context import FronteggContext
from frontegg.helpers.exceptions import UnauthenticatedException
from frontegg.helpers.logger import logger


class AccessTokenAsyncResolver(TokenResolver[IEntityWithRoles]):
    def __init__(self, authenticator: FronteggAsyncAuthenticator):
        super().__init__([TokenTypes.TenantAccessToken.value, TokenTypes.UserAccessToken.value],
                         AuthHeaderType.AccessToken.value)
        self.__init_access_token_services(authenticator)

    async def validate_token(
            self,
            token: str,
            public_key: str,
            options: Optional[IValidateTokenOptions] = None
    ) -> IEntityWithRoles:
        
        entity = super().verify_token(token, public_key)
        entity_with_roles = {}

        if options is not None and ((options.get('permissions') is not None and len(options.get('permissions')) > 0) or
                                    (options.get('roles') is not None and len(options.get('roles')) > 0)):
            entity_with_roles = await self.get_entity(entity)
            self.validate_roles_and_permissions(entity_with_roles, options)
        else:
            active_ids = await self.__get_active_access_token_ids(entity)

            if active_ids is None or entity.get('sub') not in active_ids:
                raise UnauthenticatedException()

        return {**entity_with_roles, **entity}

    async def get_entity(self, entity: IEntityWithRoles) -> IEntityWithRoles:
        service = self.__get_active_access_token_service(entity.get('type'))

        return await service.get_entity(entity)

    async def __get_active_access_token_ids(self, entity: IEntityWithRoles) -> List[str]:
        service = self.__get_active_access_token_service(entity.get('type'))

        return await service.get_active_access_token_ids()

    def __get_active_access_token_service(self, type: TokenTypes):
        resolver = None
        for _resolver in self.__access_token_services:
            if _resolver.should_handle(type):
                resolver = _resolver
                break
        if resolver is None:
            logger.error("Failed to find token resolver")
            raise UnauthenticatedException()

        return resolver

    def __init_access_token_services(self, authenticator: FronteggAsyncAuthenticator):
        http_client = HttpAsyncClient(authenticator.client_id, authenticator.api_key, '')

        cache_type = FronteggContext().options.get('access_tokens_options', {}).get('cache', {}).get('type', 'local')
        cache_options = FronteggContext().options.get('access_tokens_options', {}).get('cache', {}).get('options', {})

        if cache_type == 'redis':
            self.__access_token_services = [
                CacheUserAccessTokenAsyncService(RedisCacheManager(cache_options), RedisCacheManager(cache_options),
                                                 UserAccessTokenAsyncService(http_client)),
                CacheTenantAccessTokenAsyncService(RedisCacheManager(cache_options), RedisCacheManager(cache_options),
                                                   TenantAccessTokenAsyncService(http_client))
            ]
        else:
            self.__access_token_services = [
                CacheUserAccessTokenAsyncService(LocalCacheManager(), LocalCacheManager(),
                                                 UserAccessTokenAsyncService(http_client)),
                CacheTenantAccessTokenAsyncService(LocalCacheManager(), LocalCacheManager(),
                                                   TenantAccessTokenAsyncService(http_client))
            ]
