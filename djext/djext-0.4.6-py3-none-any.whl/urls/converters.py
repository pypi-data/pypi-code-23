class PathModelConverter(object):
    """
    Supported by Django 2.0 and up

    Pass an instance of this class to register_converter
    Examples:
        register_converter(PathModelConverter(Post), 'post')
        register_converter(PathModelConverter(Coupon, field='code', regex='[a-zA-Z0-9]+'), 'coupon')
    """
    _regex = '[0-9]+'
    _field = 'pk'

    def __init__(self, model, field=None, regex=None):
        self.model = model
        if field is not None:
            self._field = field
        if regex is not None:
            self._regex = regex

    def __call__(self, *args, **kwargs):
        return self

    @property
    def regex(self):
        return self._regex

    @property
    def field(self):
        return self._field

    def to_python(self, value):
        try:
            return self.model.objects.get(**{self.field: value})
        except self.model.DoesNotExist:
            """Doe's not silence MultipleObjectsReturned exception, that should be handled somewhere else"""
            return None

    def to_url(self, value):
        return f'{getattr(value, self.field)}'
