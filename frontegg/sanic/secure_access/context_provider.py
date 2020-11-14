import sys
from sanic import request
from frontegg import FronteggContext
from frontegg.sanic.frontegg import frontegg


def context_provider(request: request):
    try:
        user = frontegg.decode_jwt(request.headers.get('Authorization'))
        return FronteggContext(user.get('sub'), user.get('tenantId'))
    except:
        return FronteggContext('user-id', 'tenant-id')
