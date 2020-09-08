from frontegg import FronteggContext
import frontegg.flask



def context_provider(req):
    decoded = frontegg.flask.frontegg.decode_jwt(verify=False)
    return FronteggContext(decoded.get('sub'), decoded.get('tenantId'))
