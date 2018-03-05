from accern import error, util
from os.path import dirname

MODULE_PATH = dirname(__file__)
FIELD_OPTIONS = util.json.load(open("%s/data/options.json" % MODULE_PATH))

class Schema(object):
    @staticmethod
    def _validate_categorical(field, value):
        VALUE = FIELD_OPTIONS[field]['value']
        return {
            'field': field,
            'type': 'categorical',
            'value': {
                'valid': [v for v in value if v in VALUE],
                'invalid': [v for v in value if v not in VALUE]
            }
        }

    @staticmethod
    def _validate_range(field, value):
        RANGE = FIELD_OPTIONS[field]['value']
        if not isinstance(value, list):
            return {
                'field': field,
                'error': 'Invalid value type of field.'
            }
        if len(value) != 2:
            return {
                'field': field,
                'type': 'range',
                'error': '"%s" has wrong number or arguments.' % (field)
            }
        if value[1] < value[0]:
            return {
                'field': field,
                'type': 'range',
                'error': '"%s" has malformed filter option value.' % (field)
            }
        if value[0] >= RANGE[0] and value[1] <= RANGE[1]:
            return {
                'field': field,
                'type': 'range',
                'value': {
                    'valid': True,
                    'default_range': RANGE
                }
            }
        return {
            'field': field,
            'type': 'range',
            'value': {
                'valid': False,
                'default_range': RANGE
            }
        }

    @staticmethod
    def _validate_norange(field, value):
        if len(value) != 2:
            return {
                'field': field,
                'type': 'no range',
                'error': '"%s" has wrong number or arguments.' % (field)
            }
        if value[1] < value[0]:
            return {
                'field': field,
                'type': 'range',
                'error': '"%s" has malformed filter option value.' % (field)
            }
        return {
            'field': field,
            'type': 'no range'
        }

    @classmethod
    def get_fields(cls):
        return [v for v in sorted(FIELD_OPTIONS.keys()) if 'filter' in FIELD_OPTIONS[v]['method'] or 'url_param' in FIELD_OPTIONS[v]['method']]

    @classmethod
    def get_options(cls, field):
        try:
            if 'filter' in FIELD_OPTIONS[field]['method'] or 'url_param' in FIELD_OPTIONS[field]['method']:
                options = FIELD_OPTIONS[field]
                del options['method']
                return options
        except KeyError:
            raise error.SchemaError('Invalid field (%s) in filter option.' % field)

    @classmethod
    def get_url_params(cls):
        return [k for k, v in FIELD_OPTIONS.items() if 'url_param' in v['method']]

    @classmethod
    def validate_options(cls, field=None, value=None):
        if field not in FIELD_OPTIONS:
            raise error.SchemaError('Invalid field (%s) in filter option.' % field)
        if value is None:
            raise error.SchemaError('No filter option value for "%s".' % field)

        types = {
            'categorical': cls._validate_categorical,
            'norange': cls._validate_norange,
            'range': cls._validate_range,
            'other': lambda field, value: {'field': field, 'value': value}
        }
        return types[FIELD_OPTIONS[field]['type']](field, value)

    @classmethod
    def validate_schema_filters(cls, method, filters):
        if isinstance(filters, list):
            if method != 'historical':
                raise error.SchemaError('Method "%s" does not support multiple filters.' % method)
            for f in filters:
                cls.validate_schema_filters(method=method, filters=f)
            return
        for f in filters:
            if isinstance(filters[f], list) and any(isinstance(el, list) for el in filters[f]):
                for el in filters[f]:
                    resp = cls.validate_options(field=f, value=el)
                    if 'error' in resp:
                        raise error.SchemaError(resp['error'])
            else:
                resp = cls.validate_options(field=f, value=filters[f])
                if 'error' in resp:
                    raise error.SchemaError(resp['error'])

    @classmethod
    def validate_schema_select(cls, method, select):
        if not select:
            return None

        if method in ['api', 'stream']:
            if any('function' in el for el in select):
                raise error.SchemaError('Method "%s" does not support select field functions.' % method)
            if isinstance(select, list):
                if any('field' not in v for v in select):
                    raise error.SchemaError('Missing "field" in select option.')
                return [{'field': v['field'], 'alias': v.get('alias', v['field'])} for v in select]

            else:
                if 'field' not in select:
                    raise error.SchemaError('Missing "field" in select option.')
                return {'field': select['field'], 'alias': select.get('alias', select['field'])}
        else:
            try:
                if any(v["field"] == 'harvested_at' and v.get("function") is not None for v in select):
                    select = [{
                        'field': v['field'],
                        'alias': v.get('alias', v['field']),
                        'function': v.get('function', FIELD_OPTIONS[v['field']]['function'][0])
                    } for v in select]

                    if any(v['field'] == 'harvested_at' and v['alias'] != v['function'] for v in select):
                        raise error.SchemaError("Alias of harvested_at is different from it's aggregation function.")
                else:
                    select = [
                        {
                            'field': v['field'],
                            'alias': v.get('alias', v['field'])
                        } for v in select]
                return select
            except KeyError:
                raise error.SchemaError('Missing "field" in select option.')

    @classmethod
    def validate_schema(cls, method=None, schema=None):
        if schema is None:
            return None
        schema = {k.lower(): v for k, v in schema.items()}

        if method is None:
            raise error.SchemaError('Method is missing.')

        if method not in ['api', 'historical', 'stream']:
            raise error.SchemaError('Illegal usage of validate schema function.')

        if method in ['api', 'stream']:
            if 'name' in schema:
                raise error.SchemaError('Illegal "name" in %s schema.' % method)
            if 'description' in schema:
                raise error.SchemaError('Illegal "description" in %s schema.' % method)
        elif method == 'historical':
            if 'name' not in schema:
                raise error.SchemaError('Required field "name" not found in %s schema.' % method)
            if 'description' not in schema:
                raise error.SchemaError('Required field "description" not found in %s schema.' % method)

        if method in ['api', 'historical', 'stream']:
            filters = schema.get('filters', {})
            cls.validate_schema_filters(method=method, filters=filters)
            select = schema.get('select', {})
            select = cls.validate_schema_select(method=method, select=select)
            if select is not None:
                schema['select'] = select

        return schema
