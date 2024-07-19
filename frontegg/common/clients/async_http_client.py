import os
from typing import Optional
from httpx import AsyncClient, Response
from urllib.parse import urljoin

from frontegg.common.frontegg_async_authenticator import FronteggAsyncAuthenticator

timeout_in_seconds = float(os.environ.get('FRONTEGG_HTTP_TIMEOUT_IN_SECONDS') or '3')


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


class HttpAsyncClient(FronteggAsyncAuthenticator):
    def __init__(self, client_id: str, api_key: str, base_url: str):
        super(HttpAsyncClient, self).__init__(client_id=client_id, api_key=api_key)
        self.base_url = base_url
        self.client = AsyncClient()

    @classmethod
    async def create_client(cls):
        instance = await cls.create()

    async def __prepare_auth_headers(self):
        if self.should_refresh_token:
            await self.refresh_token()

        self.client.headers['x-access-token'] = self.access_token

    async def get(self,
                  url: str = '',
                  params: Optional[dict] = None,
                  tenant_id: Optional[str] = None,
                  host: Optional[str] = None,
                  headers: Optional[dict] = {}) -> Response:
        await self.__prepare_auth_headers()
        new_headers = prepare_headers(tenant_id, host, headers)

        return await self.client.get(combineUrl(self.base_url, url), params=params, headers=new_headers,
                                     timeout=timeout_in_seconds)

    async def post(self,
                   data,
                   url: str = '',
                   tenant_id: Optional[str] = None,
                   host: Optional[str] = None,
                   headers: Optional[dict] = {}
                   ) -> Response:
        await self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return await self.client.post(combineUrl(self.base_url, url), json=data, headers=new_headers,
                                      timeout=timeout_in_seconds)

    async def put(self,
                  data,
                  url: str = '',
                  tenant_id: Optional[str] = None,
                  host: Optional[str] = None,
                  headers: Optional[dict] = {}
                  ) -> Response:
        await self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return await self.client.put(combineUrl(self.base_url, url), json=data, headers=new_headers,
                                     timeout=timeout_in_seconds)

    async def delete(self,
                     url: str = '',
                     tenant_id: Optional[str] = None,
                     host: Optional[str] = None,
                     headers: Optional[dict] = {}
                     ) -> Response:
        await self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return await self.client.delete(combineUrl(self.base_url, url), headers=new_headers, timeout=timeout_in_seconds)

    async def patch(self,
                    data,
                    url: str = '',
                    tenant_id: Optional[str] = None,
                    host: Optional[str] = None,
                    headers: Optional[dict] = {}
                    ) -> Response:
        await self.__prepare_auth_headers()

        new_headers = prepare_headers(tenant_id, host, headers)
        return await self.client.patch(combineUrl(self.base_url, url), json=data, headers=new_headers,
                                       timeout=timeout_in_seconds)


__all__ = 'HttpClient'
