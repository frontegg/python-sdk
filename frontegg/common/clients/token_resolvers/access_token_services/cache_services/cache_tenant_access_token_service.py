from frontegg.common.clients.types import IEntityWithRoles, TokenTypes, ITenantAccessToken, IEmptyAccessToken
from .cache_access_token_service import CacheAccessTokenService
from frontegg.common.cache.cache_manager import CacheManager
from typing import Union, List
from frontegg.common.clients.token_resolvers.access_token_services.base_access_token_service import \
    BaseAccessTokenService


class CacheTenantAccessTokenService(CacheAccessTokenService[ITenantAccessToken]):

    def __init__(
        self,
        entity_cache_manager: CacheManager[Union[IEntityWithRoles, IEmptyAccessToken]],
        active_access_tokens_cache_manager: CacheManager[List[str]],
        access_token_service: BaseAccessTokenService[ITenantAccessToken],
    ):
        super().__init__(entity_cache_manager, active_access_tokens_cache_manager, access_token_service, TokenTypes.TenantAccessToken.value)

    def get_cache_prefix(self) -> str:
        return 'frontegg_sdk_v1_tenant_access_tokens'
