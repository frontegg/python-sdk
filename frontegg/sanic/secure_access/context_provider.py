import frontegg.sanic as __frontegg
from sanic import request
from frontegg import FronteggContext



def context_provider(request: request):
    try:
        user = __frontegg.frontegg.decode_jwt(request.headers.get('Authorization'))
        return FronteggContext(user.get('sub'), user.get('tenantId'))
    except:
        return FronteggContext('user-id', 'tenant-id')


def context_provider_with_permissions(request: request):
    try:
        user = __frontegg.frontegg.decode_jwt(request.headers.get('Authorization'))
        return FronteggContext(user.get('sub'), user.get('tenantId'), user.get('permissions'))
    except:
        return FronteggContext('user-id', 'tenant-id', [])