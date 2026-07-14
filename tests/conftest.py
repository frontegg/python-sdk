import pytest
from flask import Flask

from frontegg.flask.secure_access.with_authentication import with_authentication


def create_app():
    app = Flask('test')
    app.config['FRONTEGG_CLIENT_ID'] = 'the-client-id'
    app.config['FRONTEGG_API_KEY'] = 'my-api-key'

    @app.route('/protected')
    @with_authentication()
    def protected():
        return 'ok'

    return app


@pytest.fixture
def app():
    return create_app()
