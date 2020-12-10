from ..helpers.logger import logger


class FronteggConfig():
    client_id: str = None
    api_key: str = None

    def __init__(self, client_id: str, api_key, context_provider=None,
                 authentication_middleware=None, middleware_prefix: str = None):
        if client_id is None:
            raise Exception('client_id is required')
        if api_key is None:
            raise Exception('api_key is required')
        if context_provider is None:
            raise Exception('context_provider is required')
        if authentication_middleware is None:
            logger.warning('authentication middleware was not provided. In order to protect frontegg routes, it is recommended to provide authentication_middleware which validates the authentication of the user.')

        self.client_id = client_id
        self.api_key = api_key
        self.context_callback = context_provider
        self.authentication_middleware = authentication_middleware

        # why call "frontegg/" as well? to enable overriding the fix_middleware_prefix func with suitable func for the web framework
        self.middleware_prefix = self.fix_middleware_prefix_format(
            middleware_prefix or 'frontegg/')

    def fix_middleware_prefix_format(self, prefix: str):
        if prefix.startswith('/'):
            prefix = prefix[1:]
        if not prefix.endswith('/'):
            prefix += '/'

        return prefix
