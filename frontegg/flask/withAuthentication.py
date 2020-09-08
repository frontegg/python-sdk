from functools import wraps
import typing
from . import frontegg
from flask import abort, Response



def with_authentication(
        permission_keys: typing.Optional[list] = [],
        role_keys: typing.Optional[list] = []
):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                decoded = frontegg.decode_jwt()
                valid_permissions = all(
                    permission in decoded['permissions'] for permission in permission_keys)
                valid_roles = all(role in decoded['roles']
                                  for role in role_keys)
                if valid_permissions and valid_roles:
                    return f(*args, **kwargs)
                abort(403)
            except:
                abort(401)

        return decorated_function

    return decorator
