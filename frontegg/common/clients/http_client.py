from typing import Optional
from requests import session, Response
from ..frontegg_authenticator import FronteggAuthenticator
from urllib.parse import urljoin


def merge(first: dict, second: dict):
    return {**first, **second}


def combineUrl(base_url: str, endpoint: str):
    return urljoin(base_url, endpoint)


def prepare_headers(
        tenant_id: Optional[str] = None,
        host: Optional[str] = None,
        headers: Optional[dict] = {}):
    new_headers = {}
    if tenant_id:
        new_headers['frontegg-tenant-id'] = tenant_id
    if host:
        new_headers['frontegg-vendor-host'] = host

    return merge(new_headers, headers)


class HttpClient(FronteggAuthenticator):
    def __init__(self, client_id: str, api_key: str, base_url: str):
        super(HttpClient, self).__init__(client_id=client_id, api_key=api_key)
        self.base_url = base_url
        self.client = session()

    def __prepare_auth_headers(self):
        if self.should_refresh_vendor_token:
            self.refresh_vendor_token()

        self.client.headers['x-access-token'] = self.access_token

    def get(self,
            url: str = '',
            params: Optional[dict] = None,
            tenant_id: Optional[str] = None,
            host: Optional[str] = None,
            headers: Optional[dict] = {}) -> Response:
        self.__prepare_auth_headers()
        new_headers = prepare_headers(tenant_id, host, headers)

        return self.client.get(combineUrl(self.base_url, url), params=params, headers=new_headers)

    def post(self,
             data,
             url: str = '',
             tenant_id: Optional[str] = None,
             host: Optional[str] = None,
             headers: Optional[dict] = {}
             ) -> Response:
        self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return self.client.post(combineUrl(self.base_url, url), json=data, headers=new_headers)

    def put(self,
            data,
            url: str = '',
            tenant_id: Optional[str] = None,
            host: Optional[str] = None,
            headers: Optional[dict] = {}
            ) -> Response:
        self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return self.client.put(combineUrl(self.base_url, url), json=data, headers=new_headers)

    def delete(self,
               url: str = '',
               tenant_id: Optional[str] = None,
               host: Optional[str] = None,
               headers: Optional[dict] = {}
               ) -> Response:
        self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return self.client.delete(combineUrl(self.base_url, url), headers=new_headers)

    def patch(self,
              data,
              url: str = '',
              tenant_id: Optional[str] = None,
              host: Optional[str] = None,
              headers: Optional[dict] = {}
              ) -> Response:
        self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return self.client.patch(combineUrl(self.base_url, url), json=data, headers=new_headers)


__all__ = 'HttpClient'
