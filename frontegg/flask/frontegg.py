from frontegg.baseConfig.frontegg_proxy import FronteggProxy
from flask import (Blueprint, request, make_response, Flask)
from urllib.parse import urlparse
import typing
from .secure_access import authentication_middleware as fe_auth_middleware, context_provider as fe_context_provider
from frontegg.helpers.logger import logger

class Frontegg(FronteggProxy):
    def __init__(self):
        pass

    def init_app(
            self,
            app: Flask,
            client_id: str,
            api_key: str,
            context_provider: typing.Callable = None,
            authentication_middleware = None,
            with_secure_access: bool = False,
            middleware_prefix: str = '/frontegg',
    ):
        if with_secure_access:
            authentication_middleware = authentication_middleware or fe_auth_middleware
            context_provider = context_provider or fe_context_provider

        super(Frontegg, self).__init__(client_id, api_key, context_provider, authentication_middleware,
                                       middleware_prefix)

        frontegg_blueprint = Blueprint('frontegg', __name__, url_prefix=middleware_prefix)



        @frontegg_blueprint.route('/<path:endpoint>', methods=('GET', 'POST', 'PUT', 'DELETE', 'PATCH'))
        def middleware(endpoint):

            logger.info('got new request to frontegg: method = %s, path = %s', request.method, request.path)
            o = urlparse(request.base_url)
            response = self.proxy_request(request, method=request.method, path=request.path, host=o.hostname,
                                          params=request.args, body=request.data, cookies=request.cookies,
                                          headers=dict(request.headers))

            logger.info('got response from frontegg: status_code = %s, path = %s, traceId = %s', response.status_code, request.path, response.headers.get('frontegg-trace-id'))

            return make_response(response.content, response.status_code, response.headers)

        app.register_blueprint(frontegg_blueprint)

    @property
    def ignored_response_headers(self):
        return ['content-length', 'access-control-allow-credentials', 'access-control-allow-origin']




frontegg = Frontegg()