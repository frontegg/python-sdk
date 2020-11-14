import os
from sanic import Sanic
from frontegg.sanic import frontegg
from frontegg.sanic.secure_access import context_provider
from frontegg import FronteggContext, FronteggPermissions
from sanic_cors import CORS

app = Sanic('test')
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)


# def context_resolver(request):
#     return FronteggContext('user_id@user.com', 'my-tenant-id')


# os.environ['FRONTEGG_CLIENT_ID']
# os.environ['FRONTEGG_API_KEY']
app.config['FRONTEGG_CLIENT_ID'] = os.environ.get('FRONTEGG_CLIENT_ID')
app.config['FRONTEGG_API_KEY'] = os.environ.get('FRONTEGG_API_KEY')

frontegg.init_app(app, app.config['FRONTEGG_CLIENT_ID'],
                  app.config['FRONTEGG_API_KEY'], context_provider)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
