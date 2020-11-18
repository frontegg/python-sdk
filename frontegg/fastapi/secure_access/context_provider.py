import frontegg.fastapi.frontegg as __frontegg
from fastapi import Request
from frontegg import FronteggContext


def context_provider(request: Request):
    try:
        user = __frontegg.frontegg.decode_jwt(
            request.headers.get('Authorization'))
        return FronteggContext(user.get('sub'), user.get('tenantId'))
    except:
        return FronteggContext('user-id', 'tenant-id')
