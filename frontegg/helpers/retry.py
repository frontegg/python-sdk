from functools import wraps
from frontegg.helpers.logger import logger
from time import sleep


def retry(action, total_tries=10, retry_delay=0):
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            description = action or f'function "{f.__name__}"'
            _tries = 0
            while _tries < total_tries:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if _tries == 0:
                        logger.info('%s failed on first try', description)
                    if +_tries >= total_tries - 1:
                        logger.info(
                            '%s failed on the last retry attempt (%s)',
                            description, total_tries)
                        raise e
                    _tries += 1
                    if retry_delay > 0:
                        sleep(retry_delay)

        return func_with_retries

    return retry_decorator
