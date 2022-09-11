import frontegg.sanic as __frontegg
from sanic import request
from frontegg import FronteggContext
from frontegg.helpers.create_context import create_context



def context_provider(request: request) -> FronteggContext:
    return create_context(request.headers.get('Authorization'), False, __frontegg.frontegg.decode_jwt)


def context_provider_with_permissions(request: request) -> FronteggContext:
    return create_context(request.headers.get('Authorization'), True,  __frontegg.frontegg.decode_jwt)