import frontegg.fastapi.frontegg as __frontegg
from fastapi import Request


def context_provider(request: Request):
    try:
        user = __frontegg.frontegg.decode_jwt(request.headers.get('Authorization'))
        return {
            'user_id': user.get('sub'),
            'tenant_id': user.get('tenantId')
        }
    except:
        return {
            'user_id': None,
            'tenant_id': None
        }

