from sanic import request
from frontegg.helpers.exceptions import UnauthenticatedException
from frontegg.sanic.frontegg import frontegg


def authentication_middleware(request: request):
    try:
        frontegg.decode_jwt(
            request.headers.get('Authorization'))
        return None
    except:
        raise UnauthenticatedException()
