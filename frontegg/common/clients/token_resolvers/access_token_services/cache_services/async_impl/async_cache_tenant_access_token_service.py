from frontegg.common.clients.token_resolvers.access_token_services.cache_services.async_impl.async_cache_access_token_service import \
    CacheAccessTokenAsyncService
from frontegg.common.clients.token_resolvers.access_token_services.services.async_impl.async_access_token_service import \
    AccessTokenAsyncService
from frontegg.common.clients.types import IEntityWithRoles, TokenTypes, ITenantAccessToken, IEmptyAccessToken
from frontegg.common.cache.cache_manager import CacheManager
from typing import Union, List


class CacheTenantAccessTokenAsyncService(CacheAccessTokenAsyncService[ITenantAccessToken]):

    def __init__(
            self,
            entity_cache_manager: CacheManager[Union[IEntityWithRoles, IEmptyAccessToken]],
            active_access_tokens_cache_manager: CacheManager[List[str]],
            access_token_service: AccessTokenAsyncService[ITenantAccessToken],
    ):
        super().__init__(entity_cache_manager, active_access_tokens_cache_manager, access_token_service,
                         TokenTypes.TenantAccessToken.value)

    def get_cache_prefix(self) -> str:
        return 'frontegg_sdk_v1_tenant_access_tokens'
