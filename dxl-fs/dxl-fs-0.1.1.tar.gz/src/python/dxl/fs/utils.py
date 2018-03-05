from functools import wraps
import rx


def outputs_observable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, rx.Observable):
            return result
        return rx.Observable.from_(tuple(result))
    return wrapper
