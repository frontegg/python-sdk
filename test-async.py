import os
import aiohttp_cors
from aiohttp import web
from aiohttp_middlewares import cors_middleware

from frontegg.aiohttp import Frontegg
from frontegg import FronteggContext, FronteggPermissions


async def frontegg_context_resolver():
    # permissions = (FronteggPermissions.Teams.value.Read,)
    permissions = [FronteggPermissions.All]
    return FronteggContext('my-user-id', 'my-tenant-id', permissions=permissions)

# app = web.Application()
app = web.Application(middlewares=(
    cors_middleware(origins=("http://localhost:3000",)),))
Frontegg(app, 'my-client-id', 'my-api-key', frontegg_context_resolver)


if __name__ == '__main__':
    web.run_app(app, port=5555)
