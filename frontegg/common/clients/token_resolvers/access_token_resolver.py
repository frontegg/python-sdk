from typing import Optional, List
from frontegg.common.clients.token_resolvers.token_resolver import TokenResolver
from frontegg.common.clients.token_resolvers.access_token_services.services.user_access_token_service import UserAccessTokenService
from frontegg.common.clients.token_resolvers.access_token_services.services.tenant_access_token_service import TenantAccessTokenService
from frontegg.common.clients.token_resolvers.access_token_services.cache_services.cache_user_access_token_service import CacheUserAccessTokenService
from frontegg.common.clients.token_resolvers.access_token_services.cache_services.cache_tenant_access_token_service import CacheTenantAccessTokenService
from frontegg.common.clients.types import TokenTypes, AuthHeaderType, IEntityWithRoles, IValidateTokenOptions
from frontegg.common.cache.local_cache_manager import LocalCacheManager
from frontegg.common.cache.redis_cache_manager import RedisCacheManager
from frontegg.helpers.logger import logger
from frontegg.common import FronteggAuthenticator
from frontegg.common.clients import HttpClient
from frontegg.common.frontegg_context import FronteggContext
from frontegg.helpers.exceptions import UnauthenticatedException


class AccessTokenResolver(TokenResolver[IEntityWithRoles]):
    def __init__(self, authenticator: FronteggAuthenticator):
        super().__init__([TokenTypes.TenantAccessToken.value, TokenTypes.UserAccessToken.value], AuthHeaderType.AccessToken.value)
        self.__init_access_token_services(authenticator)

    def validate_token(
            self,
            token: str,
            public_key: str,
            options: Optional[IValidateTokenOptions] = None
    ) -> IEntityWithRoles:
        entity = super().verify_token(token, public_key)
        entity_with_roles = {}

        if options is not None and ((options.get('permissions') is not None and len(options.get('permissions')) > 0) or
                                    (options.get('roles') is not None and len(options.get('roles')) > 0)):
            entity_with_roles = self.get_entity(entity)
            self.validate_roles_and_permissions(entity_with_roles, options)
        else:
            active_ids = self.__get_active_access_token_ids(entity)
            if entity.get('sub') not in active_ids:
                raise UnauthenticatedException()

        return {**entity_with_roles, **entity}

    def get_entity(self, entity: IEntityWithRoles) -> List[str]:
        service = self.__get_active_access_token_service(entity.get('type'))

        return service.get_entity(entity)

    def __get_active_access_token_ids(self, entity: IEntityWithRoles) -> List[str]:
        service = self.__get_active_access_token_service(entity.get('type'))

        return service.get_active_access_token_ids()

    def __get_active_access_token_service(self, type: TokenTypes):
        resolver = None
        for _resolver in self.__access_token_services:
            if _resolver.should_handle(type):
                resolver = _resolver
                break
        if not resolver:
            logger.error("Failed to find token resolver")
            raise UnauthenticatedException()

        return resolver

    def __init_access_token_services(self, authenticator: FronteggAuthenticator):
        http_client = HttpClient(authenticator.client_id, authenticator.api_key, '')

        cache_type = FronteggContext().options.get('access_tokens_options', {}).get('cache', {}).get('type', 'local')
        cache_options = FronteggContext().options.get('access_tokens_options', {}).get('cache', {}).get('options', {})

        if cache_type == 'redis':
            self.__access_token_services = [
                CacheUserAccessTokenService(RedisCacheManager(cache_options), RedisCacheManager(cache_options), UserAccessTokenService(http_client)),
                CacheTenantAccessTokenService(RedisCacheManager(cache_options), RedisCacheManager(cache_options), TenantAccessTokenService(http_client))
            ]
        else:
            self.__access_token_services = [
                CacheUserAccessTokenService(LocalCacheManager(), LocalCacheManager(), UserAccessTokenService(http_client)),
                CacheTenantAccessTokenService(LocalCacheManager(), LocalCacheManager(), TenantAccessTokenService(http_client))
            ]