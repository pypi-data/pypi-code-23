from copy import deepcopy
from addict import Dict
from . import primitives


def typed(parent, type, **kwargs):
    """Adds a type to a schema and construct it (see :ref:`primitives`)

    :param parent: Schema to type
    :type parent: dict

    :param type: JSON primitive type name
    :type type: str

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))
    _schema.type = type

    primitive = getattr(primitives, type, None)

    if primitive is not None:
        _schema = primitive(_schema, **kwargs)

    return _schema


def require(parent, *keys):
    """Require properties from object.

    :param parent: Schema containing the properties
    :type parent: dict

    :param keys: Properties to require
    :type keys: List[str]

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))

    if not _schema.required:
        _schema.required = []

    for key in keys:
        if key not in _schema.required:
            _schema.required.append(key)

    return _schema


def oneOf(parent, *schemas):
    """Add a clause to validate only one of the supplied schemas.

    :param parent: Schema to add the clause to
    :type parent: dict

    :param schemas: List of schemas
    :type schemas: List[dict]

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))

    if len(schemas) > 0:
        _schema.oneOf = list(deepcopy(schemas))

    return _schema


def anyOf(parent, *schemas):
    """Add a clause to validate at least one of the supplied schemas.

    :param parent: Schema to add the clause to
    :type parent: dict

    :param schemas: List of schemas
    :type schemas: List[dict]

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))

    if len(schemas) > 0:
        _schema.anyOf = list(deepcopy(schemas))

    return _schema


def allOf(parent, *schemas):
    """Add a clause to validate all of the supplied schemas.

    :param parent: Schema to add the clause to
    :type parent: dict

    :param schemas: List of schemas
    :type schemas: List[dict]

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))

    if len(schemas) > 0:
        _schema.allOf = list(deepcopy(schemas))

    return _schema


def not_(parent, schema):
    """Add a clause to invalidate if the supplied schemas validates.

    :param parent: Schema to add the clause to
    :type parent: dict

    :param schema: Schema that must not validate the data
    :type schema: dict

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))
    _schema['not'] = Dict(deepcopy(schema))
    return _schema


def enum(parent, *values):
    """Add a clause to validate that the data takes only one of the supplied
    values.

    :param parent: Schema to add the clause to
    :type parent: dict

    :param values: Authorized values for data
    :type values: List[Any]

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))

    if len(values) > 0:
        _schema.enum = list(deepcopy(values))

    return _schema


def default(parent, value):
    """Add a clause to use a default value if none is supplied by the data.

    :param parent: Schema to add the clause to
    :type parent: dict

    :param value: Default value to use
    :type value: Any

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))
    _schema.default = deepcopy(value)
    return _schema


def dependencies(parent, **deps):
    """Add a clause to make properties dependent.

    :param parent: Schema to add the clause to
    :type parent: dict

    :param deps: Dependencies definition
    :type deps: Mapping[str, Union[dict, List[str]]]

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))
    _schema.dependencies = Dict(deepcopy(deps))
    return _schema
