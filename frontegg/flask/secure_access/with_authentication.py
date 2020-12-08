import typing
from functools import wraps
import frontegg.flask as __frontegg
from flask import request, abort


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

                # Validate roles
                if (role_keys != None):
                    valid_roles = any(
                        role in decoded['roles'] for role in role_keys)

                if (permission_keys != None):
                    valid_permissions = any(
                        permission in decoded['permissions'] for permission in permission_keys)

            except Exception as e:
                print(e)
                abort(401)

            if not valid_permissions or not valid_roles:
                abort(403)
                return

            return f(*args, **kwargs)

        return decorated_function

    return decorator
