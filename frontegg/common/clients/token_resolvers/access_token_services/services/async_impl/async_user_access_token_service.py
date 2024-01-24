from typing import List

from frontegg.common.clients import HttpAsyncClient
from frontegg.common.clients.token_resolvers.access_token_services.services.async_impl.async_access_token_service import \
    AccessTokenAsyncService
from frontegg.common.clients.types import IEntityWithRoles, TokenTypes, IUserAccessToken
from frontegg.helpers.frontegg_urls import frontegg_urls
from urllib.parse import urljoin


class UserAccessTokenAsyncService(AccessTokenAsyncService[IUserAccessToken]):
    def __init__(self, client: HttpAsyncClient):
        super().__init__(TokenTypes.UserAccessToken.value)
        self.client = client

    async def get_entity_from_identity(self, entity: IUserAccessToken) -> IEntityWithRoles:
        endpoint = urljoin('resources/vendor-only/users/access-tokens/v1/', entity.get('sub'))
        response = await self.client.get(urljoin(frontegg_urls.identity_service['base_url'], endpoint))
        response.raise_for_status()
        data = response.json()

        return {**entity, 'roles': data.get('roles'), 'permissions': data.get('permissions')}

    async def get_active_access_token_ids_from_identity(self) -> List[str]:
        response = await self.client.get(
            urljoin(frontegg_urls.identity_service['base_url'], 'resources/vendor-only/users/access-tokens/v1/active'))
        response.raise_for_status()
        data = response.json()

        return data
