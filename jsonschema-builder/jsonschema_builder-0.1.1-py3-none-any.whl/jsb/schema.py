from copy import deepcopy
from addict import Dict


def draft04():
    """Return URL for the Draft 4 meta schema."""
    return 'http://json-shema.org/draft-04/schema#'


DEFAULT_SCOPE_ID = 'id'


def schema(
    id=None,
    title=None,
    description=None,
    meta=None,
    scope_id=DEFAULT_SCOPE_ID
):
    """Create a new schema.

    :param id: Schema identifier
    :type id: str

    :param title: Schema title
    :type title: str

    :param description: Schema's description
    :type description: str

    :param meta: URL to the meta schema (see :func:`draft04`)
    :type meta: str

    :param scope_id: Key to use to store schema identifier (default: ``id``)
    :type scope_id: str

    :rtype: dict
    """

    _schema = Dict()

    if meta is not None:
        _schema['$schema'] = meta

    if id is not None:
        _schema[scope_id] = id

    if title is not None:
        _schema.title = title

    if description is not None:
        _schema.description = description

    return _schema


def define(parent, id, schema):
    """Adds a schema definition to a schema.

    :param parent: Schema that will store the new definition
    :type parent: dict

    :param id: Definition identifier
    :type id: str

    :param schema: Schema of new definition
    :type schema: dict

    :rtype: dict
    """

    _schema = Dict(deepcopy(parent))
    _schema.definitions[id] = Dict(deepcopy(schema))
    return _schema


def ref(id):
    """Return a new JSON reference to a definition in a schema.

    :param id: Definition identifier
    :type id: str

    :rtype: dict
    """

    return Dict({'$ref': '#/definitions/{0}'.format(id)})
