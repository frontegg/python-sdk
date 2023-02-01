import abc
from typing import List, Generic, TypeVar, Union
from frontegg.common.clients.types import IAccessToken, IEntityWithRoles, TokenTypes

T = TypeVar('T', bound=IAccessToken)


class BaseAccessTokenService(Generic[T]):
    def __init__(self, type: Union[TokenTypes.UserAccessToken.value, TokenTypes.TenantAccessToken.value]):
        self.type = type

    @abc.abstractmethod
    def get_entity(self, entity: T) -> IEntityWithRoles:
        pass

    @abc.abstractmethod
    def get_active_access_token_ids(self) -> List[str]:
        pass

    def should_handle(self, type: Union[TokenTypes.UserAccessToken.value, TokenTypes.TenantAccessToken.value]) -> bool:
        return self.type == type
