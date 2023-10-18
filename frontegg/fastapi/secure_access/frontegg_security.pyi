import enum
from _typeshed import Incomplete
from fastapi import Request as Request
from fastapi.security.base import SecurityBase
from frontegg.common.clients.types import AuthHeaderType as AuthHeaderType
from frontegg.helpers.exceptions import UnauthorizedException as UnauthorizedException
from frontegg.helpers.logger import logger as logger
from pydantic import BaseModel
from typing import Any, Callable, Dict, List, Optional

class TokenType(str, enum.Enum):
    UserToken: str
    UserApiToken: str
    TenantApiToken: str
    TenantAccessToken: str
    UserAccessToken: str

class User(BaseModel):
    sub: str
    roles: List[str]
    permissions: List[str]
    tenant_id: str
    token_type: TokenType
    access_token: str
    metadata: Optional[Dict[str, Any]]
    name: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    tenant_ids: Optional[List[str]]
    profile_picture_url: Optional[str]
    super_user: Optional[bool]
    created_by_user_id: Optional[str]
    def has_permissions(self, permissions: List[str]) -> bool: ...
    def has_roles(self, roles: List[str]) -> bool: ...
    @property
    def id(self) -> Optional[str]: ...

class FronteggHTTPAuthentication(SecurityBase):
    model: Incomplete
    scheme_name: Incomplete
    auto_error: Incomplete
    roles: Incomplete
    permissions: Incomplete
    def __init__(self, bearerFormat: Optional[str] = ..., scheme_name: Optional[str] = ..., auto_error: bool = ..., roles: List[str] = ..., permissions: List[str] = ...) -> None: ...
    def handle_authentication_failure(self) -> None: ...
    async def __call__(self, request: Request) -> Optional[User]: ...

def FronteggSecurity(permissions: List[str] = ..., auto_error: bool = ..., roles: List[str] = ...) -> Callable[[], User]: ...
def get_auth_header(req: Request) -> Optional[Dict[str, Any]]: ...
