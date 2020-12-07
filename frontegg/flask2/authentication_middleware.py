import frontegg.flask2
from flask import abort


def authentication_middleware(req):
    try:
        frontegg.flask2.frontegg.decode_jwt()
    except:
        abort(401)
