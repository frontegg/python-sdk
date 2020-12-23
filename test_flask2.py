from frontegg.flask.secure_access import context_provider_with_permissions, authentication_middleware, with_authentication, context_provider
from flask import Blueprint, g

more_secrets = Blueprint('more_secrets', __name__)

@more_secrets.route('/secret')
@with_authentication()
def cool():
    return g.user



app.run(port=8080)
