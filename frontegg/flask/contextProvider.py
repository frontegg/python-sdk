from frontegg import FronteggContext
import frontegg.flask



def context_provider(request):
    if request.headers.get('Authorization'):
        decoded = frontegg.flask.frontegg.decode_jwt(verify=False)
        return FronteggContext(decoded.get('sub'), decoded.get('tenantId'))

    return FronteggContext('user-id', 'tenant-id')

