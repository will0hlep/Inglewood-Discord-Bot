"""
This module implements a retry decorator for use with the
legacy_server_status_check function.
"""
from collections.abc import Callable


def retry(tries: int, on_fail) -> Callable:
    """
    Constructs a retry decorator which calls a function again if it
    raises an OSError.

    Parameters:
        tries : int
            the maximum number of times the decorated function will
            called.
        on_fail
            to be returned by the decorated function if it raises an
            OSError on all attempts.

    Returns:
        decorator : Callable
            the retry decorator function.
    """
    def decorator(func: Callable) -> Callable:
        def retry_func(*args, **kwargs):
            attempts = 0
            while attempts <= tries:
                try:
                    return func(*args, **kwargs)
                except OSError:
                    attempts += 1
            return on_fail
        return retry_func
    return decorator
