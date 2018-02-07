__version__ = '1.1.0'


_LIMIT_TO_OPERATOR = {
    'min': '>=',
    'max': '<=',
    'fix': '==',
}


def construct_where_condition(**filters):
    def _extract(key):
        col_name, limit = key.rsplit('_', 1)
        return col_name, _LIMIT_TO_OPERATOR[limit]

    condition_parts = [
        _extract(key) + (val,)
        for key, val in sorted(filters.items())
        if val is not None
    ]
    return ' & '.join(
        "(%s %s %s)" % (col, op, val)
        for col, op, val in condition_parts
    )

def read_from_table(table, **filters):
    condition = construct_where_condition(**filters)
    return table.read_where(condition) if condition else table.read()
