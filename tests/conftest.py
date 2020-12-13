import pytest
from flask import Flask

from frontegg.client import FronteggContext
from frontegg.flask2.flask import Frontegg


def create_app():
    app = Flask('test')
    app.config['FRONTEGG_CLIENT_ID'] = 'the-client-id'
    app.config['FRONTEGG_API_KEY'] = 'my-api-key'
    app.config['FRONTEGG_CONTEXT_RESOLVER'] = lambda r: FronteggContext(
        'ee@ee.eee', 'my-tenant-id')

    return app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture(autouse=True)
def frontegg(app):
    return Frontegg(app)
