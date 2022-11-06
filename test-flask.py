from flask import Flask
from frontegg.flask import frontegg
from frontegg.flask.secure_access import with_authentication
from frontegg.common.clients import AuditsClient, HttpClient, Severity
from frontegg.helpers.frontegg_urls import frontegg_urls
from flask_cors import CORS
from frontegg import frontegg_logger
import logging
from flask import g

frontegg_logger.setLevel(logging.DEBUG)

app = Flask('my-app')
CORS(app, supports_credentials=True)

client_id = os.environ['FRONTEGG_CLIENT_ID']
api_key = os.environ['FRONTEGG_API_KEY']


frontegg.init_app(client_id=client_id, api_key=api_key)

http_client = HttpClient(client_id=client_id, api_key=api_key, base_url=frontegg_urls.audits_service['base_url'])
audits_client = AuditsClient(http_client)


@app.route('/secret')
@with_authentication()
def cool():
    audits_client.send_audit(audit={'severity': Severity.INFO}, tenant_id=g.user['tenantId'])

    return {'user': g.user}


@app.route('/public')
def hello():
    return 'Hello'


app.run(host="localhost", port=8080)
