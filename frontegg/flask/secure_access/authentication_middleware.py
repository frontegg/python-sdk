from flask import Request
from frontegg.helpers.exceptions import UnauthenticatedException
import frontegg.flask as __frontegg


def authentication_middleware(request: Request):
    try:
        __frontegg.frontegg.decode_jwt(request.headers.get('Authorization'))
        return None
    except:
        raise UnauthenticatedException()
