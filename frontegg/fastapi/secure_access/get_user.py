from fastapi import HTTPException
from fastapi.security.base import SecurityBase
from fastapi import Request
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
    roles: List[str]
    permissions: List[str]
    tenant_id: str = Field(alias='tenantId')
    tenant_ids: List[str] = Field(alias='tenantIds')
    profile_picture_url: str = Field(alias='profilePictureUrl')


class GetUser(SecurityBase):
    def __init__(self,
                 bearerFormat: Optional[str] = None,    # noqa
                 scheme_name: str = None,
                 auto_error: bool = True):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[User]:
        authorization: str = request.headers.get("Authorization")
        try:
            decoded = frontegg.fastapi.frontegg.decode_jwt(authorization)
            return User(**decoded)
        except InvalidTokenError:
            if self.auto_error:
                raise HTTPException(
                    status_code=401, detail="Unauthenticated"
                )
            else:
                return None


get_user = GetUser(auto_error=True)
