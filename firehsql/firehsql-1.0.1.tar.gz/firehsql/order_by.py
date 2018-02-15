class OrderByMixin(object):

    _order_fields = None

    def __init__(self):
        super(OrderByMixin, self).__init__()
        self._order_fields = []


    def set_sorting_order(self, *expressions):
        for expression in expressions:
            is_desc = expression.startswith('-')
            if is_desc:
                field = self.field(expression[1:])
            else:
                field = self.field(expression)

            # This is a mixin, so self.schema came from SQL
            self.validate_order_field_name(field)
            self._order_fields.append((field, is_desc))


    @property
    def order_fields(self):
        return list(self.get_order_fields())


    def get_order_fields(self):
        for field, is_desc in self._order_fields:
            if is_desc:
                yield str(field) + ' DESC'
            else:
                yield str(field)


    def clear_order_by(self):
        self._order_fields = []


    def find_sorting_order(self, data, fields):
        if data is None:
            return

        db_fields = []
        form_fields = []
        for field in fields:
            if isinstance(field, (list, tuple)):
                db_fields.append(field[0])
                form_fields.append(field[1])
            else:
                db_fields.append(field)
                form_fields.append(field)

        for expression in data:
            is_desc = expression.startswith('-')
            if is_desc:
                field = expression[1:]
            else:
                field = expression

            try:
                idx = form_fields.index(field)
                if form_fields[idx] == db_fields[idx]:
                    yield expression
                elif is_desc:
                    yield '-' + db_fields[idx]
                else:
                    yield db_fields[idx]
            except ValueError:
                pass
