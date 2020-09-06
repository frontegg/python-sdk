from functools import wraps
import jwt
import typing
from flask import make_response, request
from . import frontegg


def with_authentication(
        permission_keys: typing.Optional[list] = [],
        role_keys: typing.Optional[list] = []
):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            authorization_header = request.headers.get('Authorization')
            if not authorization_header:
                return make_response('Unauthorized', 401)
            jwt_token = authorization_header.replace('Bearer ', '')
            try:
                public_key = frontegg.getPublicKey()
                decoded = jwt.decode(jwt_token, public_key, algorithms='RS256')
                request.user = decoded
                valid_permissions = all(
                    permission in decoded['permissions'] for permission in permission_keys)
                valid_roles = all(role in decoded['roles']
                                  for role in role_keys)
                if valid_permissions and valid_roles:
                    return f(*args, **kwargs)
                return make_response('Forbidden', 403)
            except:
                return make_response('Unauthorized', 401)

        return decorated_function

    return decorator
