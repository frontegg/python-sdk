from fastapi.security.base import SecurityBase
from fastapi import Request, Depends, HTTPException
from typing import Optional, Any, Dict, List
from jwt import PyJWTError
import frontegg
from pydantic import BaseModel, Field
from fastapi.security.http import HTTPBearerModel
import enum
from frontegg.helpers.logger import logger


class TokenType(str, enum.Enum):
    UserToken = 'userToken'
    UserApiToken = 'userApiToken'
    TenantApiToken = 'tenantApiToken'


class User(BaseModel):
    # Fields which are general for all kind of tokens
    sub: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    tenant_id: str = Field(alias='tenantId')
    metadata: Dict[str, Any]
    token_type: TokenType = Field(alias='type')
    access_token: str

    # User token fields - all fields must be optional in order to support API tokens
    name: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    tenant_ids: Optional[List[str]] = Field(alias='tenantIds', default_factory=list)
    profile_picture_url: Optional[str] = Field(alias='profilePictureUrl')

    # API Token fields - all fields must be optional in order to support user tokens
    created_by_user_id: Optional[str] = Field(alias='createdByUserId')

    def has_permissions(self, permissions: List[str]) -> bool:
        return bool(permissions) and all(p in self.permissions for p in permissions)

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
                 auto_error: bool = True):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    def handle_authentication_failure(self):
        if self.auto_error:
            raise HTTPException(
                status_code=401, detail="Unauthenticated"
            )
        else:
            return None

    async def __call__(self, request: Request) -> Optional[User]:
        authorization: str = request.headers.get("Authorization")
        try:
            decoded = frontegg.fastapi.frontegg.decode_jwt(authorization)
            return User(**decoded, access_token=authorization.replace('Bearer ', ''))
        except PyJWTError:
            self.handle_authentication_failure()
        except Exception as e:
            logger.warning(f"Cought unexpected exception when decoding user's token: {repr(e)}")
            self.handle_authentication_failure()


def FronteggSecurity(permissions: List[str] = None, auto_error: bool = True):  # noqa
    """
    This factory function will create authentication dependency for FastAPI,
    and will ensure the user has the right permissions if specified.
    """

    def check_perm(user: User = Depends(FronteggHTTPAuthentication(auto_error=auto_error))):
        if permissions and not user.has_permissions(permissions=permissions):
            raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
        return user

    return check_perm
