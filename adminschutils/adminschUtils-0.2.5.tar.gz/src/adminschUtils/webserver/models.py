def get_model(data: type):
    model = BaseConsume
    model.data = data
    return model


class ConsumeMeta(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        if not hasattr(cls, 'data') and cls.__name__ != 'BaseConsume':
            raise NotImplementedError('Request model should have data attribute')
        return super().__init__(name, bases, attrs)


class BaseConsume(metaclass=ConsumeMeta):
    access_token = str
