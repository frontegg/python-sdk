from frontegg import FronteggContext
from frontegg.helpers.logger import logger
from frontegg.helpers.jwt_types import jwt_types
import typing


def create_context(authorization_header: str, with_permissions: bool,
                   decode_jwt_func: typing.Callable) -> FronteggContext:
    try:
        entity = decode_jwt_func(authorization_header)
        logger.debug('get user from JWT' + str(entity))
        jwt_type = entity.get('type')
        permissions = None
        if with_permissions:
            permissions = entity.get('permissions')

        if jwt_type == jwt_types['tenant_api_token']:
            return FronteggContext(None, entity.get('tenantId'), permissions, jwt_type, entity.get('sub'))
        elif jwt_type == jwt_types['user_api_token']:
            return FronteggContext(entity.get('createdByUserId'), entity.get('tenantId'), permissions, jwt_type,
                                   entity.get('sub'))
        return FronteggContext(entity.get('sub'), entity.get('tenantId'), permissions, entity.get('type'),
                               entity.get('sub'))
    except Exception as e:
        logger.debug('could not get user from JWT, ' + str(e))
        logger.info('will send default tenant-id and user-id')
        if with_permissions:
            return FronteggContext('user-id', 'tenant-id', [], jwt_types['user'], 'user-id')
        return FronteggContext('user-id', 'tenant-id', None, jwt_types['user'], 'user-id')
