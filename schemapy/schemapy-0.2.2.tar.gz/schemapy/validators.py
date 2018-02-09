def IS_OF(cls):
    def validator(value):
        if not isinstance(value, cls):
            return (
                value,
                f'expected {cls.__name__}, got {value.__class__.__name__}'
            )

        else:
            return (value, None)

    return validator


def IS_GREATER_THAN(val):
    def validator(value):
        if value <= val:
            return (value, f'{value} <= {val}')

        else:
            return (value, None)

    return validator


def IS_LESS_THAN(val):
    def validator(value):
        if value >= val:
            return (value, f'{value} >= {val}')

        else:
            return (value, None)

    return validator


def IS_GREATER_THAN_OR_EQUAL(val):
    def validator(value):
        if value < val:
            return (value, f'{value} < {val}')

        else:
            return (value, None)

    return validator


def IS_LESS_THAN_OR_EQUAL(val):
    def validator(value):
        if value > val:
            return (value, f'{value} > {val}')

        else:
            return (value, None)

    return validator


def IS_IN_RANGE(minimum, maximum):
    def validator(value):
        if minimum <= value <= maximum:
            return (value, None)

        else:
            return (value, f'{value} not in [{minimum};{maximum}]')

    return validator


def IS_LENGTH(val):
    def validator(value):
        if len(value) > val:
            return (value, 'maximum length exceed')

        else:
            return (value, None)

    return validator
