import os
from flask import Flask
from frontegg.flask import frontegg
from frontegg.flask.secure_access import context_provider_with_permissions, authentication_middleware, with_authentication, context_provider
from flask_cors import CORS
from frontegg import frontegg_logger
import logging
from flask import g


frontegg_logger.setLevel(logging.DEBUG)

app = Flask('my-app')
CORS(app, supports_credentials=True)

client_id = os.environ['FRONTEGG_CLIENT_ID']
api_key = os.environ['FRONTEGG_API_KEY']


frontegg.init_app(app=app, client_id=client_id, api_key=api_key,
                  context_provider=context_provider_with_permissions, with_secure_access=True)


@app.route('/secret')
@with_authentication()
def cool():
    return g.user


app.run(port=8080)
