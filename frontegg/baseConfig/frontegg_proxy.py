from frontegg.baseConfig.frontegg_authenticator import FronteggAuthenticator
from frontegg.helpers.frontegg_urls import frontegg_urls
from urllib.parse import urljoin
import typing
from frontegg.helpers.frontegg_headers import frontegg_headers
from frontegg.helpers.exceptions import HttpException
from .identity_mixin import IdentityClientMixin
from frontegg.helpers.logger import logger
from werkzeug.datastructures import Headers
from http.cookies import SimpleCookie

class FronteggProxy(FronteggAuthenticator, IdentityClientMixin):
    __routes_config = None

    def proxy_request(self, request, method: str, path: str, host: str, params: dict,
                      body: typing.Optional[any], cookies: typing.Optional[dict] = None,
                      headers: typing.Optional[dict] = {}):
        if not request:
            raise Exception('request is required')

        if not method:
            raise Exception('method is required')

        if not path:
            raise Exception('path is required')

        path_without_frontegg = path.replace(
            '/' + self.middleware_prefix, '', 1).replace(self.middleware_prefix, '', 1)

        logger.info('removed path prefix before sending to frontegg, new path - %s', path_without_frontegg)

        public_route = self.is_public_route(
            path_without_frontegg, params, method)

        logger.info('route is %s public route', '' if public_route else 'not')

        if self.authentication_middleware is not None and not public_route:
            try:
                logger.info('will validate user authentication')
                self.authentication_middleware(request)
            except HttpException as response:
                logger.info('failed to authorize entity')
                return response
            except Exception as e:
                logger.info('something went wrong, could not run authentication middleware')
                logger.debug('auth middleware error - %s', str(e))
                return HttpException('Something went wrong', 500)

        url = urljoin(frontegg_urls.base_url, path_without_frontegg)
        headers = self.clean_request_headers(headers, host)
        headers = self.set_context(headers, request)
        logger.info('adjusted headers before proxying request to frontegg')
        logger.debug('new headers - %s', str(headers))

        if self.should_refresh_vendor_token:
            logger.info('refresh vendor token is required, will refresh token')
            self.refresh_vendor_token()

        logger.info('will proxy request to frontegg')
        logger.debug('request data: method=%s, url=%s,cookies=%s, body=%s, params=%s, headers=%s', method, url,
                     str(cookies), str(body), str(params), str(headers))
        response = self.vendor_session_request.request(
            method,
            url,
            headers=headers,
            cookies=cookies,
            data=body,
            params=params
        )

        logger.info('got response from frontegg')

        response.headers = self.clean_response_headers(response.headers)

        return response

    def clean_request_headers(self, headers: dict, host: str) -> dict:
        new_headers = dict()
        ignored_headers = ['host', 'authorization']
        for key, value in headers.items():
            if 'access-control' not in key.lower() and key.lower() not in ignored_headers:
                new_headers[key] = value

        new_headers[frontegg_headers['vendor_host']] = host
        return new_headers

    def clean_response_headers(self, headers: dict) -> dict:
        new_headers = Headers()

        ignored_headers = self.ignored_response_headers

        for key, value in headers.items():
            if key.lower() in ignored_headers:
                continue

            if key == "set-cookie":
                cookie = SimpleCookie()
                cookie.load(value)
                for cookieKey, morsel in cookie.items():
                    new_headers.add(key, morsel.OutputString().replace(',', ''))
            else:
                new_headers.add(key, value)

        return new_headers

    @property
    def ignored_response_headers(self):
        return ['access-control-allow-credentials', 'access-control-allow-origin']


    def set_context(self, headers: dict, request) -> dict:
        context = self.context_callback(request)
        headers[frontegg_headers['middleware_request']] = 'True'
        if context.tenant_id is not None:
            headers[frontegg_headers['tenant_id']] = context.tenant_id
        if context.user_id is not None:
            headers[frontegg_headers['user_id']] = context.user_id
        if context.permissions is not None:
            headers[frontegg_headers['permissions']] = ','.join(context.permissions)
        return headers

    @property
    def routes_config(self):
        if self.__routes_config:
            return self.__routes_config
        response = self.vendor_session_request.get(frontegg_urls.routes_config)

        self.__routes_config = response.json()
        return self.__routes_config

    def is_public_route(self, path: str, params: dict, method: str) -> bool:
        public_routes = self.routes_config['vendorClientPublicRoutes']

        for route in public_routes:
            if path != route['url']:
                continue
            if method != route['method'].upper():
                continue
            if route.get('withQueryParams'):
                is_valid = True
                for query_param in route['withQueryParams']:
                    value = params.get(query_param['key'])
                    if not value:
                        is_valid = False
                        break
                    if query_param.get('value') and value != query_param['value']:
                        is_valid = False
                        break

                if not is_valid:
                    continue
            return True
        return False
