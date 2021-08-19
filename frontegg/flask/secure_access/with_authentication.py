import typing
from functools import wraps
import frontegg.flask as __frontegg
from flask import request, abort
from frontegg.helpers.logger import logger
from flask import g


def with_authentication(
        permission_keys: typing.Optional[list] = None,
        role_keys: typing.Optional[list] = None
):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Initially
            valid_permissions = True
            valid_roles = True
            try:
                decoded = __frontegg.frontegg.decode_jwt(request.headers.get('Authorization'))
                g.user = decoded
                # Validate roles
                if role_keys is not None:
                    logger.info('will check if entity has one of required roles')
                    valid_roles = any(
                        role in decoded['roles'] for role in role_keys)

                if permission_keys is not None:
                    logger.info('will check if entity has one of required permissions')
                    valid_permissions = any(
                        permission in decoded['permissions'] for permission in permission_keys)

            except Exception as e:
                logger.info('something went wrong while validating JWT, ' + str(e))
                abort(401)

            if not valid_permissions or not valid_roles:
                logger.info('entity does not have required role and permissions')
                abort(403)
                return

            logger.info('entity passed authentication middleware')

            return f(*args, **kwargs)

        return decorated_function

    return decorator
