from fastapi.security.base import SecurityBase
from fastapi import Request, Depends, HTTPException
from typing import Optional, Any, Dict, List
import frontegg
from pydantic import BaseModel, Field
from fastapi.security.http import HTTPBearerModel
import enum
from frontegg.helpers.logger import logger
from frontegg.common.clients.types import AuthHeaderType
from frontegg.helpers.exceptions import UnauthorizedException


class TokenType(str, enum.Enum):
    UserToken = 'userToken'
    UserApiToken = 'userApiToken'
    TenantApiToken = 'tenantApiToken'
    TenantAccessToken = 'tenantAccessToken'
    UserAccessToken = 'userAccessToken'


class User(BaseModel):
    # Fields which are general for all kind of tokens
    sub: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    tenant_id: str = Field(alias='tenantId')

    token_type: TokenType = Field(alias='type')
    access_token: str

    # User token fields - all fields must be optional in order to support API tokens
    metadata: Optional[Dict[str, Any]]
    name: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    tenant_ids: Optional[List[str]] = Field(alias='tenantIds', default_factory=list)
    profile_picture_url: Optional[str] = Field(alias='profilePictureUrl')
    super_user: Optional[bool] = Field(alias='superUser')

    # API Token fields - all fields must be optional in order to support user tokens
    created_by_user_id: Optional[str] = Field(alias='createdByUserId')

    def has_permissions(self, permissions: List[str]) -> bool:
        return bool(permissions) and all(p in self.permissions for p in permissions)

    def has_roles(self, roles: List[str]) -> bool:
        return bool(roles) and all(r in self.roles for r in roles)

    @property
    def id(self) -> Optional[str]:
        """
        When using tenant API Token, there is no user ID.
        When using user API Token, the user ID specified in the created_by_user_id field.
        Otherwise, the user ID is specified in the sub field.
        """
        if self.token_type == TokenType.TenantApiToken:
            return None

        return self.created_by_user_id or self.sub


class FronteggHTTPAuthentication(SecurityBase):
    def __init__(self,
                 bearerFormat: Optional[str] = None,  # noqa
                 scheme_name: str = None,
                 auto_error: bool = True,
                 roles: List[str] = [],
                 permissions: List[str] = []):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error
        self.roles = roles
        self.permissions = permissions

    def handle_authentication_failure(self):
        if self.auto_error:
            raise HTTPException(
                status_code=401, detail="Unauthenticated"
            )
        else:
            return None

    async def __call__(self, request: Request) -> Optional[User]:
        try:
            auth_header = get_auth_header(request)
            if auth_header is None:
                raise HTTPException(status_code=401, detail="Unauthenticated")

            decoded_user = frontegg.fastapi.frontegg.validate_identity_on_token(
                auth_header.get('token'),
                {'roles': self.roles, 'permissions': self.permissions},
                auth_header.get('type')
            )
            return User(**decoded_user, access_token=auth_header.get('token'))

        except UnauthorizedException:
            logger.info('entity does not have required role and permissions')
            raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')

        except Exception as e:
            logger.error('something went wrong while validating JWT, ' + str(e))
            return self.handle_authentication_failure()


def FronteggSecurity(permissions: List[str] = None, auto_error: bool = True, roles: List[str] = None):  # noqa
    """
    This factory function will create authentication dependency for FastAPI,
    and will ensure the user has the right permissions if specified.
    """

    def check_perm(user: User = Depends(FronteggHTTPAuthentication(auto_error=auto_error, roles=roles, permissions=permissions))):
        return user

    return check_perm


def get_auth_header(req):
    token = req.headers.get('Authorization')
    if token is not None:
        return {'token': token.replace('Bearer ', ''), 'type': AuthHeaderType.JWT.value}

    token = req.headers.get('x-api-key')
    if token is not None:
        return {'token': token, 'type': AuthHeaderType.AccessToken.value}

    return None
