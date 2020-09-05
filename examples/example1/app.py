import os
from flask import Flask, make_response
from frontegg import FronteggContext
from frontegg.flask import frontegg, withAuthentication
from flask_cors import CORS
from examples.example1.secretsApi import secretsApi


app = Flask('example1')
CORS(app, supports_credentials=True)

app.config['FRONTEGG_CLIENT_ID'] = os.environ['FRONTEGG_CLIENT_ID']
app.config['FRONTEGG_API_KEY'] = os.environ['FRONTEGG_API_KEY']
app.config['FRONTEGG_CONTEXT_RESOLVER'] = lambda request: FronteggContext(
    'my-user-id', 'my-tenant-id')

frontegg.init_app(app)

app.register_blueprint(secretsApi)

@app.route('/secret')
@withAuthentication()
def cool():
    return make_response('here is a secret - python is lit!', 200)


app.run()
