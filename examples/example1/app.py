import os
from flask import Flask, make_response
from frontegg.flask import frontegg
from frontegg.flask.secure_access import with_authentication
from flask_cors import CORS
from examples.example1.secretsApi import secretsApi

app = Flask('example1')
CORS(app, supports_credentials=True)

clientId = os.environ['FRONTEGG_CLIENT_ID']
apiKey = os.environ['FRONTEGG_API_KEY']

frontegg.init_app(clientId=clientId, apiKey=apiKey)

app.register_blueprint(secretsApi)


@app.route('/secret')
@with_authentication()
def cool():
    return make_response('here is a secret - python is lit!', 200)


app.run()
