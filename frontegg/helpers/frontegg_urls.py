import os
from urllib.parse import urljoin
from typing import Dict


class FronteggUrls:

    def __init__(self):
        self.__base_url = os.environ.get('FRONTEGG_HOSTED_LOGIN_URL', 'https://api.frontegg.com/')
        self.__identity_base_url = os.environ.get('FRONTEGG_IDENTITY_SERVICE_URL', urljoin(self.base_url, 'identity/'))

    @property
    def base_url(self) -> str:
        if not self.__base_url.endswith('/'):
            self.__base_url = self.__base_url + '/'
        return self.__base_url

    @property
    def authentication_service(self) -> Dict[str, str]:
        return {
            'authenticate': urljoin(self.__identity_base_url, 'resources/auth/v2/api-token'),
            'refresh_token': urljoin(self.__identity_base_url, 'resources/auth/v1/api-token/token/refresh')
        }

    @property
    def identity_service(self) -> Dict[str, str]:
        return {
            'base_url': self.__identity_base_url,
            'vendor_config': urljoin(self.__identity_base_url, 'resources/configurations/v1')
        }


frontegg_urls = FronteggUrls()

__all__ = 'frontegg_urls'
