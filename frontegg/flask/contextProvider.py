from frontegg import FronteggContext
from flask import request
import jwt


def context_provider(req):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return FronteggContext('', '')
    jwt_token = authorization_header.replace('Bearer ', '')
    decoded = jwt.decode(jwt_token, algorithms='RS256', verify=False)
    request.user = decoded
    return FronteggContext(decoded.get('sub'), decoded.get('tenantId'))
