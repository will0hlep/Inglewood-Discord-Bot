def retry(tries, on_fail):
    def decorator(func):
        def retry_func(*args, **kwargs):
            attempts = 0
            while attempts <= tries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
            return on_fail
        return retry_func
    return decorator