from copy import deepcopy
from addict import Dict


def object(
    parent,
    properties=None,
    additionalProperties=None,
    patternProperties=None,
    minProperties=None,
    maxProperties=None
):
    """
    :param properties: Object properties
    :type properties: Mapping[str, dict]

    :param additionalProperties: (Dis)allow additional properties on data
    :type additionalProperties: Union[bool, dict]

    :param patternProperties: Object properties that match a regular expression
    :type patternProperties: Mapping[str, dict]

    :param minProperties: Minimum number of properties on data
    :type minProperties: int

    :param maxProperties: Maximum number of properties on data
    :type minProperties: int
    """

    _schema = Dict(deepcopy(parent))

    if properties is not None:
        for propname, propschema in properties.items():
            _schema.properties[propname] = Dict(deepcopy(propschema))

    if additionalProperties is not None:
        _schema.additionalProperties = deepcopy(additionalProperties)

    if patternProperties is not None:
        for propname, propschema in patternProperties.items():
            _schema.patternProperties[propname] = Dict(deepcopy(propschema))

    if minProperties is not None:
        _schema.minProperties = minProperties

    if maxProperties is not None:
        _schema.maxProperties = maxProperties

    return _schema


def array(
    parent,
    items=None,
    additionalItems=None,
    minItems=None,
    maxItems=None,
    uniqueItems=None
):
    """
    :param items: Array item schema
    :type items: Union[List[dict], dict]

    :param additionalItems: (Dis)allow additional items on data
    :type additionalProperties: Union[bool, dict]

    :param minItems: Minimum number of items on data
    :type minItems: int

    :param maxItems: Maximum number of items on data
    :type minItems: int

    :param uniqueItems: Specify if all items must be unique
    :type uniqueItems: bool
    """

    _schema = Dict(deepcopy(parent))

    if items is not None:
        _schema['items'] = deepcopy(items)

    if additionalItems is not None:
        _schema.additionalItems = deepcopy(additionalItems)

    if minItems is not None:
        _schema.minItems = minItems

    if maxItems is not None:
        _schema.maxItems = maxItems

    if uniqueItems is not None:
        _schema.uniqueItems = uniqueItems

    return _schema


def string(
    parent,
    minLength=None,
    maxLength=None,
    pattern=None,
    format=None
):
    """
    :param minLength: Minimum length of string
    :type minLength: int

    :param maxLength: Maximum length of string
    :type maxLength: int

    :param pattern: Regular expression the string must validate
    :type pattern: str

    :param format: String format (see JSON schema specification)
    :type format: str
    """

    _schema = Dict(deepcopy(parent))

    if minLength is not None:
        _schema.minLength = minLength

    if maxLength is not None:
        _schema.maxLength = maxLength

    if pattern is not None:
        _schema.pattern = pattern

    if format is not None:
        _schema.format = format

    return _schema


def number(
    parent,
    minimum=None,
    maximum=None,
    exclusiveMinimum=None,
    exclusiveMaximum=None,
    multipleOf=None
):
    """
    :param minimum: Minimum value authorized
    :type minimum: float

    :param maximum: Maximum value authorized
    :type maximum: float

    :param exclusiveMinimum: Is the minimum value authorized?
    :type exclusiveMinimum: bool

    :param exclusiveMaximum: Is the maximum value authorized?
    :type exclusiveMaximum: bool

    :param multipleOf: Number that must be a divisor of the supplied data
    :type multipleOf: float
    """

    _schema = Dict(deepcopy(parent))

    if minimum is not None:
        _schema.minimum = minimum

    if maximum is not None:
        _schema.maximum = maximum

    if exclusiveMinimum is not None:
        _schema.exclusiveMinimum = exclusiveMinimum

    if exclusiveMaximum is not None:
        _schema.exclusiveMaximum = exclusiveMaximum

    if multipleOf is not None:
        _schema.multipleOf = multipleOf

    return _schema


integer = number
