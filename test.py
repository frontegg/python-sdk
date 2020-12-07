import os
from flask import Flask, make_response
from frontegg import FronteggContext
from frontegg.flask import frontegg
from flask_cors import CORS


app = Flask('example1')
CORS(app, supports_credentials=True)

app.config['FRONTEGG_CLIENT_ID'] = '697cf7dc-848c-4195-b86c-ac8e08d5bf1f'
app.config['FRONTEGG_API_KEY'] = '303af577-d565-4209-95e0-5ad8f4e3c0c9'
app.config['FRONTEGG_CONTEXT_RESOLVER'] = lambda request: FronteggContext(
    'my-user-id', 'my-tenant-id')


def context_provider(request):
    return FronteggContext('my-user-id', 'my-tenant-id')

frontegg.init_app(app=app, client_id='697cf7dc-848c-4195-b86c-ac8e08d5bf1f', api_key='303af577-d565-4209-95e0-5ad8f4e3c0c9', context_provider=context_provider)


@app.route('/secret')
def cool():
    return make_response('here is a secret - python is lit!', 200)


app.run(port=8080)
