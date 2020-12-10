import frontegg.fastapi.frontegg as __frontegg
from fastapi import Request
from frontegg import FronteggContext
from frontegg.helpers.logger import logger

def context_provider(request: Request):
    try:
        user = __frontegg.frontegg.decode_jwt(
            request.headers.get('Authorization'))
        logger.info('decoded entity')
        return FronteggContext(user.get('sub'), user.get('tenantId'))
    except:
        return FronteggContext('user-id', 'tenant-id')


def context_provider_with_permissions(request: Request):
    try:
        user = __frontegg.frontegg.decode_jwt(
            request.headers.get('Authorization'))
        logger.info('decoded entity with permissions')
        return FronteggContext(user.get('sub'), user.get('tenantId'), user.get('permissions'))
    except:
        return FronteggContext('user-id', 'tenant-id', [])
