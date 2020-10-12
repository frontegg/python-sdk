from frontegg import FronteggContext
import frontegg.flask

def context_provider(request):
    if request.get('user'):
        return FronteggContext(request.user.get('sub'), request.user.get('tenantId'))

    return FronteggContext('user-id', 'tenant-id')

