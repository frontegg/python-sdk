from functools import wraps
from frontegg.helpers.logger import logger


def retry(action, total_tries=10):
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries = 0
            while _tries < total_tries:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if _tries == 0:
                        logger.info((action or f'function "{f.__name__}"') + f' failed on first try, {e}')
                    if +_tries >= total_tries - 1:
                        logger.info((action or f'function "{f.__name__}"') + f' failed on the last retry attempt ({total_tries}), {e}')
                        raise e
                    _tries += 1

        return func_with_retries

    return retry_decorator
