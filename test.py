import os
from flask import Flask, make_response
from frontegg.flask import frontegg
from frontegg.flask.secure_access import context_provider_with_permissions, authentication_middleware, with_authentication
from flask_cors import CORS

app = Flask('example1')
CORS(app, supports_credentials=True)



frontegg.init_app(app=app, client_id='697cf7dc-848c-4195-b86c-ac8e08d5bf1f',
                  api_key='303af577-d565-4209-95e0-5ad8f4e3c0c9', context_provider=context_provider_with_permissions,
                  authentication_middleware=authentication_middleware)


@app.route('/secret')
@with_authentication(role_keys=['delete'], permission_keys=['dsadsa'])
def cool():
    return make_response('here is a secret - python is lit!', 200)


app.run(port=8080)
