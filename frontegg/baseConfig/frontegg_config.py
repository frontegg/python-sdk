import typing


class FronteggConfig():
    client_id: str = None
    api_key: str = None

    def __init__(self, client_id: str, api_key, context_provider: typing.Callable = None,
                 authentication_middleware=None, middleware_prefix: str = 'frontegg/'):
        if client_id is None:
            raise Exception('client_id is required')
        if api_key is None:
            raise Exception('api_key is required')
        if context_provider is None:
            raise Exception('context_provider is required')

        self.client_id = client_id
        self.api_key = api_key
        self.context_callback = context_provider
        self.authentication_middleware = authentication_middleware
        self.middleware_prefix = middleware_prefix
