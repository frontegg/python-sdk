import typing
from functools import wraps
import frontegg.flask as __frontegg
from flask import request, abort
from frontegg.helpers.logger import logger
from flask import g
from frontegg.common.clients.types import AuthHeaderType
from frontegg.helpers.exceptions import UnauthorizedException


def with_authentication(
        permission_keys: typing.Optional[list] = None,
        role_keys: typing.Optional[list] = None
):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Initially
            try:
                auth_header = get_auth_header(request)
                if auth_header is None:
                    abort(401)
                    return

                decoded_user = __frontegg.frontegg.validate_identity_on_token(
                    auth_header.get('token'),
                    {'roles': role_keys, 'permissions': permission_keys},
                    auth_header.get('type')
                )
                g.user = decoded_user

            except UnauthorizedException:
                logger.info('entity does not have required role and permissions')
                abort(403)

            except Exception as e:
                logger.info('something went wrong while validating JWT, ' + str(e))
                abort(401)

            logger.info('entity passed authentication middleware')

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_auth_header(req):
    token = req.headers.get('Authorization')
    if token is not None:
        return {'token': token.replace('Bearer ', ''), 'type': AuthHeaderType.JWT.value}

    token = req.headers.get('x-api-key');
    if token is not None:
        return {'token': token, 'type': AuthHeaderType.AccessToken.value}

    return None
