from fastapi import HTTPException
from fastapi.security.base import SecurityBase
from fastapi import Request
from typing import Optional
from frontegg.fastapi import frontegg


class GetUser(SecurityBase):
    def __init__(self, scheme_name: str = None, auto_error: bool = True):
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        try:
            decoded = frontegg.decode_jwt(authorization)
            return decoded
        except:
            if self.auto_error:
                raise HTTPException(
                    status_code=401, detail="Unauthenticated"
                )
            else:
                return None


get_user = GetUser(auto_error=True)
