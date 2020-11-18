from sanic import request, response
from frontegg import FronteggContext, FronteggPermissions
from frontegg.baseConfig.frontegg_proxy import FronteggProxy
import typing

RequestT = typing.TypeVar('RequestT')


class Frontegg(FronteggProxy):
    def __init__(self):
        pass

    async def handler(self, request, path):
        body = request.body
        host = request.headers.get('host') or request.client.host
        host = host.split(':')[0]

        response_from_proxy = self.proxy_request(request=request, method=request.method, path=path,
                                                 host=host, body=body, headers=request.headers,
                                                 params=request.args)
        return response.raw(
            response_from_proxy.content,
            headers=response_from_proxy.headers,
            status=response_from_proxy.status_code
        )

    def init_app(
            self,
            app,
            client_id: str,
            api_key: str,
            context_provider=None,
            authentication_middleware=None,
            middleware_prefix: str = '/frontegg',
    ):

        super(Frontegg, self).__init__(client_id, api_key,
                                       context_provider,
                                       authentication_middleware,
                                       middleware_prefix)

        routeUrl = middleware_prefix + '/<path:[^/].*?>'
        app.add_route(self.handler, routeUrl, methods=(
            'GET', 'POST', 'PUT', 'DELETE', 'PATCH'))


frontegg = Frontegg()
