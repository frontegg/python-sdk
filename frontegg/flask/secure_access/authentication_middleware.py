from flask import Request
from frontegg.helpers.exceptions import UnauthenticatedException
from frontegg.helpers.logger import logger
import frontegg.flask as __frontegg


def authentication_middleware(request: Request):
    try:
        __frontegg.frontegg.decode_jwt(request.headers.get('Authorization'))
        logger.info('JWT token verified')
        return None
    except Exception as e:
        logger.debug('could not verify JWT token, ' + str(e), )
    raise UnauthenticatedException()
