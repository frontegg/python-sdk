from fastapi.security.base import SecurityBase
from fastapi import Request, Depends, HTTPException
from typing import Optional
from jwt import InvalidTokenError
import frontegg
from pydantic import BaseModel, Field
from typing import List
from fastapi.security.http import HTTPBearerModel


class User(BaseModel):
    sub: str
    name: str
    email: str
    email_verified: bool
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    tenant_id: str = Field(alias='tenantId')
    tenant_ids: List[str] = Field(alias='tenantIds', default_factory=list)
    profile_picture_url: str = Field(alias='profilePictureUrl')
    access_token: str

    def has_permissions(self, permissions: List[str]) -> bool:
        return bool(permissions) and all(p in self.permissions for p in permissions)


class FronteggHTTPAuthentication(SecurityBase):
    def __init__(self,
                 bearerFormat: Optional[str] = None,  # noqa
                 scheme_name: str = None,
                 auto_error: bool = True):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[User]:
        authorization: str = request.headers.get("Authorization")
        try:
            decoded = frontegg.fastapi.frontegg.decode_jwt(authorization)
            return User(**decoded, access_token=authorization.replace('Bearer ', ''))
        except InvalidTokenError:
            if self.auto_error:
                raise HTTPException(
                    status_code=401, detail="Unauthenticated"
                )
            else:
                return None


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
