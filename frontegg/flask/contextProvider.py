from frontegg import FronteggContext
import frontegg.flask


def context_provider(request):
    if hasattr(request, 'user'):
        return FronteggContext(request.user.get('sub'), request.user.get('tenantId'))

    return FronteggContext('user-id', 'tenant-id')
