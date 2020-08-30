import os
import typing
from urllib.parse import urljoin

import aiohttp
import arrow
from frontegg import FronteggContext, FronteggPermissions
from aiohttp.web import middleware, Request
from aiohttp import web, ClientSession

from frontegg.permissions import validate_permissions, ForbiddenRequest
from frontegg.conf import FronteggApiUrls


class FronteggAuthenticationClient:

    async def authenticate(self,
                           session: typing.Optional[ClientSession]):

        # print('going to authenticate with frontegg')
        response = await session.post(FronteggApiUrls['authentication_service'],
                                      json={'clientId': self.client_id,
                                            'secret': self.api_key})

        # print('got response data')
        auth_response_data = await response.json()
        # print(auth_response_data)

        self.access_token = auth_response_data['token']
        self.access_token_expiry = arrow.utcnow().shift(
            seconds=auth_response_data['expiresIn'] * 0.8)

    async def get_access_token(self):
        async with aiohttp.ClientSession() as session:
            if self.access_token is None or self.access_token_expiry is None or arrow.utcnow() >= self.access_token_expiry:
                await self.authenticate(session)

        return self.access_token

    def __init__(self,
                 client_id: typing.Optional[str],
                 api_key: typing.Optional[str]):

        self.client_id = client_id
        self.api_key = api_key
        self.access_token = None
        self.access_token_expiry = None


class Frontegg:

    @staticmethod
    async def proxy_request(
            request: typing.Optional[Request],
            session: typing.Optional[ClientSession],
            context: FronteggContext,
            access_token: str,
            request_url: str):

        # print('in proxy request')

        # Format the path
        api_url = urljoin(FronteggApiUrls['gateway'], request_url)

        # Set the headers
        headers = {
            'x-access-token': access_token,
        }

        if context.tenant_id:
            headers['frontegg-tenant-id'] = context.tenant_id

        if context.user_id:
            headers['frontegg-user-id'] = context.user_id

        # Get the body to send
        json = None
        if request.body_exists and request.can_read_body:
            json = await request.json()

        # print('Going to proxy request')
        response = await session.request(method=request.method, url=api_url, headers=headers, json=json)
        # print('Done proxying request')
        return response

    async def fronteggHandler(self, request):
        async with aiohttp.ClientSession() as session:
            # Get the authentication token from the client
            access_token = await self.authenticator.get_access_token()

            # Call await for the context resolver lambda to resolve the tenantId and user_id
            context = await self.context_resolver(request)
            # print(context.user_id)
            # print(context.tenant_id)

            # Check the permissions
            if context:
                permissions = context.permissions
            else:
                permissions = (FronteggPermissions.All,)

            request_url = str(request.url.path_qs).replace('/frontegg/', '/')
            try:
                validate_permissions(
                    request_url, request.method, permissions=permissions)
            except ForbiddenRequest:
                return web.json_response({'message': "Forbidden"}, status=403)

            # Proxy the call to our API GW (you should take the URL of the API gateway via the os.env)
            response = await self.proxy_request(request, session, context, access_token, request_url)
            response_data = await response.json()
            # print(response_data)
            # print(len(response_data))
            return web.json_response(response_data)

    @middleware
    async def middleware(self, request, handler):
        # print(request)
        # print(request.url)
        # print(request.url.path)

        if '/frontegg/' in request.url.path:
            response = await self.fronteggHandler(request)
            return response

        return await handler(request)

    def __init__(self,
                 app: typing.Optional[web.Application],
                 client_id: str,
                 api_key: str,
                 context_resolver: typing.Optional[FronteggContext]):
        """
        :param app:
        :param client_id:
        :param api_key:
        :param context_resolver:
        """

        self.client_id = client_id
        self.api_key = api_key
        self.context_resolver = context_resolver
        self.authenticator = FronteggAuthenticationClient(client_id, api_key)

        app.middlewares.append(self.middleware)
