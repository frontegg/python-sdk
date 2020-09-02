import os
from flask import Flask, make_response
from frontegg import FronteggContext
from frontegg.flask import Frontegg
from flask_cors import CORS

print()

app = Flask('example')
CORS(app, supports_credentials=True)

app.config['FRONTEGG_CLIENT_ID'] = os.environ['FRONTEGG_CLIENT_ID']
app.config['FRONTEGG_API_KEY'] = os.environ['FRONTEGG_API_KEY']
app.config['FRONTEGG_CONTEXT_RESOLVER'] = lambda request: FronteggContext(
    'my-user-id', 'my-tenant-id')

frontegg = Frontegg(app)

@app.route('/secret')
@frontegg.withAuthentication()
def cool():
    return make_response('here is a secret - python is lit!', 200)


app.run()
