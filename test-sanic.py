from sanic import Sanic
import os
from frontegg.sanic import frontegg
from frontegg.sanic.secure_access import context_provider_with_permissions, with_authentication, authentication_middleware
from sanic_cors import CORS
from sanic.response import json


app = Sanic('test')
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)


client_id = os.environ.get('FRONTEGG_CLIENT_ID')
api_key = os.environ.get('FRONTEGG_API_KEY')

frontegg.init_app(app, client_id, api_key, with_secure_access=True, context_provider=context_provider_with_permissions)


@app.route('/secret')
@with_authentication()
def cool(request):
    return json(request.ctx.user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
