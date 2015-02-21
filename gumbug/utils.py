import traceback
import logging
import time
import random
from django.conf import settings


def do_with_retry(func, *args, **kwargs):
    """ Tries a function settings.RETRY_COUNT times using exponential backoff
        according to Google API specs. If a 'retry_count' kwargs is passed in
        then that is used instead.
    """
    last_exc = None
    retry_count = kwargs.pop('retry_count', getattr(settings, 'RETRY_COUNT', 3))

    for n in range(retry_count):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            logging.exception(e)
            last_exc = e
            # back off by factor of two plus a random number of milliseconds
            # to prevent deadlocks (according to API docs..)
            time.sleep(2 ** n + random.randint(0, 1000) / 1000)
    if not last_exc or not isinstance(last_exc, BaseException):
        raise Exception("%s" % last_exc)
    else:
        raise last_exc
