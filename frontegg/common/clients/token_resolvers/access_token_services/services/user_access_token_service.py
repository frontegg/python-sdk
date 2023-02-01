from typing import List
from frontegg.common.clients.types import IEntityWithRoles, TokenTypes, IUserAccessToken
from .access_token_service import AccessTokenService
from frontegg.common.clients.http_client import HttpClient
from frontegg.helpers.frontegg_urls import frontegg_urls
from urllib.parse import urljoin


class UserAccessTokenService(AccessTokenService[IUserAccessToken]):
    def __init__(self, client: HttpClient):
        super().__init__(TokenTypes.UserAccessToken.value)
        self.client = client

    def get_entity_from_identity(self, entity: IUserAccessToken) -> IEntityWithRoles:
        endpoint = urljoin('resources/vendor-only/users/access-tokens/v1/', entity.get('sub'))
        response = self.client.get(urljoin(frontegg_urls.identity_service['base_url'], endpoint))
        data = response.json()

        return {**entity, 'roles': data.get('roles'), 'permissions': data.get('permissions')}

    def get_active_access_token_ids_from_identity(self) -> List[str]:
        response = self.client.get(
            urljoin(frontegg_urls.identity_service['base_url'], 'resources/vendor-only/users/access-tokens/v1/active'))
        data = response.json()

        return data
