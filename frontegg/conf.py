import os
from urllib.parse import urljoin


FronteggApiUrls = dict()

FronteggApiUrls['gateway'] = os.environ.get('FRONTEGG_API_GATEWAY_URL', 'https://api.frontegg.com/')

FronteggApiUrls['authentication_service'] = os.environ.get('FRONTEGG_AUTHENTICATION_SERVICE_URL',
                                                           urljoin(FronteggApiUrls['gateway'], '/auth/vendor'))

FronteggApiUrls['audits_service'] = os.environ.get('FRONTEGG_AUDITS_SERVICE_URL',
                                                   urljoin(FronteggApiUrls['gateway'], '/audits'))

FronteggApiUrls['metadata'] = os.environ.get('FRONTEGG_METADATA_SERVICE_URL',
                                             urljoin(FronteggApiUrls['gateway'], '/metadata'))

FronteggApiUrls['identity'] = os.environ.get('FRONTEGG_IDENTITY_SERVICE_URL',
                                             urljoin(FronteggApiUrls['gateway'], '/identity'))


__all__ = ('FronteggApiUrls',)
