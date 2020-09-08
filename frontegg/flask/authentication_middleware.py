import frontegg.flask
from flask import abort


def authentication_middleware(req):
    try:
        frontegg.flask.frontegg.decode_jwt()
    except:
        abort(401)
