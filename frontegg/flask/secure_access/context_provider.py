import frontegg.flask as __frontegg
from flask import Request
from frontegg import FronteggContext
from frontegg.helpers.logger import logger

def context_provider(request: Request):
    try:
        user = __frontegg.frontegg.decode_jwt(
            request.headers.get('Authorization'))
        logger.debug('get user from JWT' + str(user))
        return FronteggContext(user.get('sub'), user.get('tenantId'))
    except Exception as e:
        logger.debug('could not get user from JWT, ' + str(e))
        logger.info('will send default tenant-id and user-id')
        return FronteggContext('user-id', 'tenant-id')


def context_provider_with_permissions(request: Request):
    try:
        user = __frontegg.frontegg.decode_jwt(
            request.headers.get('Authorization'))
        logger.debug('get user from JWT' + str(user))
        return FronteggContext(user.get('sub'), user.get('tenantId'), user.get('permissions'))
    except Exception as e:
        logger.debug('could not get user from JWT, ' + str(e))
        logger.info('will send default tenant-id,user-id and empty permissions')
        return FronteggContext('user-id', 'tenant-id', [])