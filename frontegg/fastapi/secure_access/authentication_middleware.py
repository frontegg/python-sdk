from fastapi import Request
from frontegg.fastapi import frontegg
from frontegg.helpers.exceptions import UnauthenticatedException


def authentication_middleware(request: Request):
    try:
        frontegg.decode_jwt(request.headers.get('Authorization'))
        return None
    except:
        raise UnauthenticatedException()
