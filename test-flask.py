import os
from flask import Flask, make_response
from frontegg.flask import frontegg
from frontegg.flask.secure_access import context_provider_with_permissions, authentication_middleware, with_authentication
from flask_cors import CORS
from frontegg import frontegg_logger
import logging


frontegg_logger.setLevel(logging.DEBUG)

app = Flask('example1')
CORS(app, supports_credentials=True)

clientId = os.environ['FRONTEGG_CLIENT_ID']
apiKey = os.environ['FRONTEGG_API_KEY']



frontegg.init_app(app=app, client_id=clientId, api_key=apiKey, context_provider=context_provider_with_permissions, with_secure_access=True)


@app.route('/secret')
@with_authentication(role_keys=['readonly'])
def cool():
    return make_response('here is a secret - python is lit!', 200)



app.run(port=8080)
