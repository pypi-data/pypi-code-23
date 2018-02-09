def IS_OF(cls):
    def validator(value):
        if not isinstance(value, cls):
            return (
                value,
                'expected {0}, got {1}'.format(
                    cls.__name__,
                    value.__class__.__name__
                )
            )

        else:
            return (value, None)

    return validator


def IS_GREATER_THAN(val):
    def validator(value):
        if value <= val:
            return (value, '{0} <= {1}'.format(value, val))

        else:
            return (value, None)

    return validator


def IS_LESS_THAN(val):
    def validator(value):
        if value >= val:
            return (value, '{0} >= {1}'.format(value, val))

        else:
            return (value, None)

    return validator


def IS_GREATER_THAN_OR_EQUAL(val):
    def validator(value):
        if value < val:
            return (value, '{0} < {1}'.format(value, val))

        else:
            return (value, None)

    return validator


def IS_LESS_THAN_OR_EQUAL(val):
    def validator(value):
        if value > val:
            return (value, '{0} > {1}'.format(value, val))

        else:
            return (value, None)

    return validator


def IS_IN_RANGE(minimum, maximum):
    def validator(value):
        if minimum <= value <= maximum:
            return (value, None)

        else:
            return (
                value,
                '{0} not in [{1};{2}]'.format(value, minimum, maximum)
            )

    return validator


def IS_LENGTH(val):
    def validator(value):
        if len(value) > val:
            return (value, 'maximum length exceed')

        else:
            return (value, None)

    return validator
