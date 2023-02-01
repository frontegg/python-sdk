from enum import Enum
from typing import Dict, List, Optional, Union


class AuthHeaderType(Enum):
    JWT = 'JWT'
    AccessToken = 'AccessToken'


class AuthHeader:
    token: str
    type: AuthHeaderType


class IValidateTokenOptions:
    roles: Optional[List[str]] = None
    permissions: Optional[List[str]] = None


class TokenTypes(Enum):
    UserApiToken = 'userApiToken'
    TenantApiToken = 'tenantApiToken'
    UserToken = 'userToken'
    TenantAccessToken = 'tenantAccessToken'
    UserAccessToken = 'userAccessToken'


Role = str
Permission = str


class IEntity:
    id: Optional[str] = None
    sub: str
    tenantId: str
    type: TokenTypes


class IEntityWithRoles(IEntity):
    roles: List[Role]
    permissions: List[Permission]


class IEmptyAccessToken:
    empty: True


class IUser(IEntityWithRoles):
    type: TokenTypes.UserToken
    metadata: Dict[str, any]
    userId: str
    name: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    invisible: Optional[bool] = None
    tenantId: str


class IAccessToken(IEntity):
    type: Union[TokenTypes.TenantAccessToken.value, TokenTypes.UserAccessToken.value]


class ITenantAccessToken(IAccessToken):
    type: TokenTypes.TenantAccessToken


class IUserAccessToken(IAccessToken):
    type: TokenTypes.UserAccessToken
    userId: str
