import sys

from comet_ml import config


def fit_logger(real_fit):
    def wrapper(*args, **kwargs):
        if config.experiment and config.experiment.disabled_monkey_patching is False:
            callback = config.experiment.get_keras_callback()
            if 'callbacks' in kwargs and kwargs['callbacks'] is not None:
                # Only append the callback if it's not there.
                if not any(x.__class__ == callback.__class__
                           for x in kwargs['callbacks']):
                    kwargs['callbacks'].append(callback)
            else:
                kwargs['callbacks'] = [callback]

        return real_fit(*args, **kwargs)

    return wrapper


def patch(module_finder):
    module_finder.register('keras.models', 'Model.fit', fit_logger)


if "keras" in sys.modules:
    raise SyntaxError("Please import Comet before importing any keras modules")
