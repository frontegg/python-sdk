from flask import request


def authentication_middleware(request: Request):
    try:
        __frontegg.frontegg.decode_jwt(request.headers.get('Authorization'))
        return None
    except:
        raise UnauthenticatedException()
