import os
from urllib.parse import urljoin
from typing import Dict

class FronteggUrls():
    __base_url = os.environ.get('FRONTEGG_API_GATEWAY_URL', 'https://api.frontegg.com/')

    def __init__(self):
        self.__authentication_base_url = os.environ.get('FRONTEGG_AUTHENTICATION_SERVICE_URL',
                                                                urljoin(self.base_url, 'auth/'))
        self.__audits_base_url = os.environ.get('FRONTEGG_AUDITS_SERVICE_URL',
                                                        urljoin(self.base_url, 'audits/'))
        self.__metadata_base_url = os.environ.get('FRONTEGG_METADATA_SERVICE_URL', urljoin(self.base_url, 'metadata/'))
        self.__identity_base_url = os.environ.get('FRONTEGG_IDENTITY_SERVICE_URL', urljoin(self.base_url, 'identity/'))

    @property
    def base_url(self) -> str:
        return self.__base_url

    @property
    def authentication_service(self) -> Dict[str, str]:
        return {
            'base_url': self.__authentication_base_url,
            'authenticate_vendor': urljoin(self.__authentication_base_url, 'vendor/')
        }

    @property
    def audits_service(self) -> Dict[str, str]:
        return {
            'base_url': self.__audits_base_url
        }

    @property
    def metadata_service(self) -> Dict[str, str]:
        return {
            'base_url': self.__metadata_base_url
        }

    @property
    def identity_service(self) -> Dict[str, str]:
        return {
            'base_url': self.__identity_base_url,
            'vendor_config': urljoin(self.__identity_base_url, 'resources/configurations/v1/')
        }

    @property
    def routes_config(self)-> str:
        return urljoin(self.__base_url, '/configs/routes')

frontegg_urls = FronteggUrls()

__all__ = 'frontegg_urls'
