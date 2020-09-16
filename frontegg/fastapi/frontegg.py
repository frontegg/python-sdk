from fastapi import FastAPI, Request, Response
from frontegg.baseConfig.frontegg_proxy import FronteggProxy
import typing
import frontegg.fastapi.secure_access as secure_access


class Frontegg(FronteggProxy):
    def __init__(self):
        pass

    def init_app(
            self,
            app: FastAPI,
            client_id: str,
            api_key,
            context_provider: typing.Callable = None,
            authentication_middleware=None,
            with_secure_access: bool = False
    ):

        if with_secure_access:
            context_provider = context_provider or secure_access.context_provider
            authentication_middleware = authentication_middleware or secure_access.authentication_middleware

        super(Frontegg, self).__init__(client_id, api_key, context_provider, authentication_middleware)

        @app.middleware('http')
        async def middleware(request: Request, call_next):
            path = request.url.path
            if path.startswith('/frontegg/'):
                body = await request.body()
                response = self.proxy_request(request=request, method=request.method, path=path,
                                              host=request.client.host, body=body, headers=request.headers,
                                              params=request.query_params)
                return Response(content=response.content, status_code=response.status_code, headers=response.headers)
            else:
                response = await call_next(request)
                return response


frontegg = Frontegg()
