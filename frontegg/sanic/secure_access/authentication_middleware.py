from sanic import request
from frontegg.helpers.exceptions import UnauthenticatedException
import frontegg.sanic as __frontegg


def authentication_middleware(request: request):
    try:
        __frontegg.frontegg.decode_jwt(
            request.headers.get('Authorization'))
        return None
    except:
        raise UnauthenticatedException()
