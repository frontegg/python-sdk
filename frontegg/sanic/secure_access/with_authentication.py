import typing
from functools import wraps
from sanic.exceptions import abort
from frontegg.sanic.frontegg import frontegg


def with_authentication(
        permission_keys: typing.Optional[list] = None,
        role_keys: typing.Optional[list] = None
):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                decoded = frontegg.decode_jwt()

                # Initially
                valid_permissions = True
                valid_roles = True

                # Validate roles
                if (role_keys != None):
                    valid_roles = any(
                        role in decoded['roles'] for role in role_keys)

                if (permission_keys != None):
                    valid_permissions = any(
                        permission in decoded['permissions'] for permission in permission_keys)

                if valid_permissions and valid_roles:
                    return f(*args, **kwargs)
                abort(403)
            except:
                abort(401)

        return decorated_function

    return decorator
