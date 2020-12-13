"""A REST client for the Frontegg API."""

import typing
from abc import ABCMeta, abstractmethod
from urllib.parse import urljoin, urlparse

import arrow
import requests

from frontegg._mixins import AuditsClientMixin, SSOClientMixin
from frontegg.permissions import FronteggPermissions, validate_permissions

RequestT = typing.TypeVar('RequestT')


class FronteggContext:
    """Request context."""

    __slots__ = ('_user_id', '_tenant_id', '_permissions')

    def __init__(self,
                 user_id: str,
                 tenant_id: str,
                 permissions: typing.List[str] = None) -> None:
        """

        :param user_id:
        :param tenant_id:
        :param permissions:
        """
        self._user_id = user_id
        self._tenant_id = tenant_id
        self._permissions = permissions

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    @property
    def permissions(self) -> typing.List[str]:
        return self._permissions


class BaseFronteggClient(typing.Generic[RequestT], metaclass=ABCMeta):
    """A REST client for the Frontegg API."""
    __routes_config = None

    def __init__(self,
                 client_id: str,
                 api_key: str,
                 context_callback: typing.Optional[typing.Callable[[
                     RequestT], FronteggContext]] = None,
                 auth_middleware: typing.Callable[[
                     RequestT], FronteggContext] = None,
                 ) -> None:
        """Initialize the Frontegg client.

        :param client_id: The client ID provided to you by Frontegg
        :param api_key: The secret key provided to you by Frontegg
        :param context_callback: A callable which accepts the current request as an argument
            and returns the frontegg context based on the request.
        """
        self.api_key = api_key
        self.client_id = client_id
        self.context_callback = context_callback
        self.auth_middleware = auth_middleware
        self.session = requests.Session()
        self._api_token = None
        self._expires_in = None

    def _maybe_refresh_api_token(self) -> None:
        """Refresh the API token if it is not present or about to expire."""
        if self._api_token is None or self._expires_in is None or arrow.utcnow() >= self._expires_in:
            self._refresh_api_token()

    def _refresh_api_token(self) -> None:
        """Refresh the API token.

        This function retrieves a new API token from the Frontegg API.

        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        """
        auth_response = self.session.post(self.authentication_service_url,
                                          json={
                                              'clientId': self.client_id,
                                              'secret': self.api_key
                                          })
        auth_response.raise_for_status()

        auth_response_data = auth_response.json()
        self._api_token = auth_response_data['token']
        self._expires_in = arrow.utcnow().shift(
            seconds=auth_response_data['expiresIn'] * 0.8)

    @property
    def routes_config(self):
        if self.__routes_config:
            return self.__routes_config
        response = self.request(
            urljoin(self.base_url, '/configs/routes'), 'GET')

        self.__routes_config = response.json()
        return self.__routes_config

    def is_public_route(self) -> bool:
        request = self.current_request
        public_routes = self.routes_config['vendorClientPublicRoutes']
        request_path = request.path.replace('/frontegg/', '')

        for route in public_routes:
            if request_path != route['url']:
                continue
            if request.method.upper() != route['method'].upper():
                continue
            if route.get('withQueryParams'):
                is_valid = True
                for query_param in route['withQueryParams']:
                    value = request.args.get(query_param['key'])
                    if not value:
                        is_valid = False
                        break
                    if query_param['value'] and value != query_param['value']:
                        is_valid = False
                        break

                if not is_valid:
                    continue
            return True
        return False

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @property
    @abstractmethod
    def authentication_service_url(self) -> str:
        pass

    @property
    def api_token(self) -> str:
        """The API Token to use to authenticate against Frontegg's services.

        :return: The API token.
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        """
        self._maybe_refresh_api_token()
        return self._api_token

    @property
    @abstractmethod
    def current_request(self) -> RequestT:
        pass

    @property
    def context(self) -> typing.Optional[FronteggContext]:
        """The context under which the request is proxied.

        :return: The :class:`FronteggContext` result from the callback.
        """
        context = None
        if self.context_callback:
            context = self.context_callback(self.current_request)

        return context

    def request(self,
                endpoint: str,
                method: str,
                json: typing.Optional[dict] = None,
                params: typing.Optional[dict] = None,
                tenant_id: typing.Optional[str] = None,
                host: typing.Optional[str] = None,
                is_vendor_request: typing.Optional[bool] = False,
                headers: typing.Optional[dict] = {}) -> requests.Response:
        """Perform a request to Frontegg's API.

        :param endpoint: The endpoint to perform the request to.
        :param method: The HTTP method to use while performing the request.
        :param data: When performing a GET request, the query string to pass as part of the request, if applicable..
            In any other request, the JSON payload to pass as the body of the request, if applicable.
        :param tenant_id: Override the tenant id from the context.
        :return: The response of the request.
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        """
        context = self.context
        if tenant_id:
            user_id = None
        else:
            if context:
                user_id, tenant_id = context.user_id, context.tenant_id
            else:
                user_id, tenant_id = None, None

        if context:
            permissions = context.permissions
        else:
            permissions = (FronteggPermissions.All,)
        validate_permissions(endpoint, method, permissions=permissions)

        newHeaders = {}
        if headers.get('Cookie'):
            newHeaders['Cookie'] = headers['Cookie']
        newHeaders['x-access-token'] = self.api_token
        newHeaders['frontegg-vendor-host'] = host

        if tenant_id and not is_vendor_request:
            newHeaders['frontegg-tenant-id'] = tenant_id
        if user_id:
            newHeaders['frontegg-user-id'] = user_id

        return self.session.request(
            method,
            urljoin(self.base_url, endpoint),
            allow_redirects=False,
            headers=newHeaders,
            json=json,
            params=params)


class FronteggRESTClient(BaseFronteggClient[None]):
    """A standalone Frontegg REST client."""

    def __init__(self,
                 client_id: str,
                 api_key: str,
                 context_callback: typing.Optional[typing.Callable[[
                     RequestT], FronteggContext]] = None,
                 base_url: str = 'https://api.frontegg.com/',
                 authentication_service_url: typing.Optional[str] = None) -> None:
        """Initialize the Frontegg REST client.

        :param client_id: The client ID provided to you by Frontegg.
        :param api_key: The secret key provided to you by Frontegg.
        :param context_callback: A callable which returns the user id and tenant id based on the current request.
        :param base_url: The base URL of the API.
        :param authentication_service_url: The URL for authenticating against Frontegg.
        """
        super().__init__(client_id, api_key, context_callback)
        self._base_url = base_url

        if authentication_service_url:
            self._authentication_service_url = authentication_service_url
        else:
            self._authentication_service_url = urljoin(
                base_url, '/vendors/auth/token')

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def authentication_service_url(self) -> str:
        return self._authentication_service_url

    @property
    def current_request(self):
        return None


class FronteggClient(SSOClientMixin, AuditsClientMixin):
    def __init__(self,
                 client_id: str,
                 api_key: str,
                 context_callback: typing.Optional[typing.Callable[[
                     RequestT], FronteggContext]] = None,
                 base_url: str = 'https://api.frontegg.com/',
                 authentication_service_url: typing.Optional[str] = None,
                 audits_service_url: typing.Optional[str] = None,
                 metadata_service_url: typing.Optional[str] = None,
                 team_service_url: typing.Optional[str] = None) -> None:
        """Initialize the Frontegg client.

        :param client_id: The client ID provided to you by Frontegg.
        :param api_key: The secret key provided to you by Frontegg.
        :param context_callback: A callable which returns the user id and tenant id based on the current request.
        :param base_url: The base URL of the API.
        :param authentication_service_url: The URL for authenticating against Frontegg.
        """
        self._client = FronteggRESTClient(
            client_id, api_key, context_callback, base_url, authentication_service_url)

        if audits_service_url:
            self._audits_service_url = audits_service_url
        else:
            self._audits_service_url = urljoin(base_url, '/audits')

        if metadata_service_url:
            self._metadata_service_url = metadata_service_url
        else:
            self._metadata_service_url = urljoin(base_url, '/metadata')

        if team_service_url:
            self._team_service_url = team_service_url
        else:
            self._team_service_url = urljoin(base_url, '/team')

    @property
    def _config(self) -> dict:
        return {
            'FRONTEGG_AUDITS_SERVICE_URL': self._audits_service_url,
            'FRONTEGG_METADATA_SERVICE_URL': self._metadata_service_url,
            'FRONTEGG_TEAM_SERVICE_URL': self._team_service_url
        }


__all__ = ('BaseFronteggClient', 'FronteggRESTClient', 'FronteggClient')
