from accern import Schema, error
import pytest


def test_fails_get_options_with_invalid_field_name():
    with pytest.raises(error.SchemaError) as exc_info:
        Schema.get_options(field='test')
    assert exc_info.value.args[0] == 'Invalid field (test) in filter option.'


def test_get_url_params():
    resp = Schema.get_url_params()
    assert len(resp) == 15

############################################################
# Test Cases for func: validate_options                    #
############################################################


def test_fails_with_invalid_field():
    with pytest.raises(error.SchemaError) as exc_info:
        Schema.validate_options(field='test')
    assert exc_info.value.args[0] == 'Invalid field (test) in filter option.'


def test_fails_without_value():
    with pytest.raises(error.SchemaError) as exc_info:
        Schema.validate_options(field='entity_ticker')
    assert exc_info.value.args[0] == 'No filter option value for "entity_ticker".'


def test_fails_range_malformed_value():
    resp = Schema.validate_options(field='entity_sentiment', value=[0, -5])
    assert resp['error'] == '"entity_sentiment" has malformed filter option value.'


def test_fails_range_with_more_argument_value():
    resp = Schema.validate_options(field='entity_sentiment', value=[0, -5, 11])
    assert resp['error'] == '"entity_sentiment" has wrong number or arguments.'


def test_fails_range_with_less_argument_value():
    resp = Schema.validate_options(field='entity_sentiment', value=[11])
    assert resp['error'] == '"entity_sentiment" has wrong number or arguments.'


def test_fails_no_range_malformed_value():
    resp = Schema.validate_options(field='story_traffic', value=[0, -5])
    assert resp['error'] == '"story_traffic" has malformed filter option value.'


def test_fails_no_range_with_more_argument_value():
    resp = Schema.validate_options(field='story_traffic', value=[0, -5, 11])
    assert resp['error'] == '"story_traffic" has wrong number or arguments.'


def test_fails_no_range_with_less_argument_value():
    resp = Schema.validate_options(field='story_traffic', value=[11])
    assert resp['error'] == '"story_traffic" has wrong number or arguments.'


############################################################
# Test Cases for func: validate_schema                     #
############################################################


def test_fails_without_method():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {}
        Schema.validate_schema(schema=schema)
    assert exc_info.value.args[0] == 'Method is missing.'


def test_with_empty_schema():
    schema = Schema.validate_schema(method='api')
    assert schema is None


def test_uppercase_schema():
    schema = {
        'FILTERS': {
            'entity_sentiment': [0, 10]
        },
        'SELECT': [
            {
                'field': 'entity_sentiment'
            }
        ]
    }
    schema = Schema.validate_schema(method='api', schema=schema)
    assert schema == {
        'filters': {'entity_sentiment': [0, 10]},
        'select': [{'alias': 'entity_sentiment', 'field': 'entity_sentiment'}]
    }

############################################################
# Test cases for func: validate_schema, method: api        #
############################################################


def test_fails_with_less_argument_value_in_filters():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'filters': {
                'entity_sentiment': [
                    [0, 10],
                    [15]
                ]
            }
        }
        Schema.validate_schema(method='api', schema=schema)
    assert exc_info.value.args[0] == '"entity_sentiment" has wrong number or arguments.'


def test_fails_with_name_in_api_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'name': 'test'
        }
        Schema.validate_schema(method='api', schema=schema)
    assert exc_info.value.args[0] == 'Illegal "name" in api schema.'


def test_fails_with_description_in_api_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'description': 'test'
        }
        Schema.validate_schema(method='api', schema=schema)
    assert exc_info.value.args[0] == 'Illegal "description" in api schema.'


def test_fails_with_multiple_filters_in_api_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'filters': [
                {
                    'entity_sentiment': [0, 10]
                },
                {
                    'entity_sentiment': [50, 100]
                }
            ]
        }
        Schema.validate_schema(method='api', schema=schema)
    assert exc_info.value.args[0] == 'Method "api" does not support multiple filters.'


def test_fails_with_select_function_in_api_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'select': [
                {
                    'field': 'harvested_at',
                    'alias': 'month',
                    'function': 'month'
                }
            ]
        }
        Schema.validate_schema(method='api', schema=schema)
    assert exc_info.value.args[0] == 'Method "api" does not support select field functions.'


def test_fails_with_missing_field_in_select_function_in_api_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'select': [
                {
                    'alias': 'harvested_at'
                }
            ]
        }
        Schema.validate_schema(method='api', schema=schema)
    assert exc_info.value.args[0] == 'Missing "field" in select option.'

############################################################
# Test cases for func: validate_schema, method: stream     #
############################################################


def test_fails_with_name_in_stream_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'name': 'test'
        }
        Schema.validate_schema(method='stream', schema=schema)
    assert exc_info.value.args[0] == 'Illegal "name" in stream schema.'


def test_fails_with_description_in_stream_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'description': 'test'
        }
        Schema.validate_schema(method='stream', schema=schema)
    assert exc_info.value.args[0] == 'Illegal "description" in stream schema.'


def test_fails_with_multiple_filters_in_stream_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'filters': [
                {
                    'entity_sentiment': [0, 10]
                },
                {
                    'entity_sentiment': [50, 100]
                }
            ]
        }
        Schema.validate_schema(method='stream', schema=schema)
    assert exc_info.value.args[0] == 'Method "stream" does not support multiple filters.'


def test_fails_with_select_function_in_stream_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'select': [
                {
                    'field': 'harvested_at',
                    'alias': 'month',
                    'function': 'month'
                }
            ]
        }
        Schema.validate_schema(method='stream', schema=schema)
    assert exc_info.value.args[0] == 'Method "stream" does not support select field functions.'


def test_fails_with_missing_field_in_select_function_in_stream_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'select': [
                {
                    'alias': 'harvested_at'
                }
            ]
        }
        Schema.validate_schema(method='stream', schema=schema)
    assert exc_info.value.args[0] == 'Missing "field" in select option.'

############################################################
# Test cases for func: validate_schema, method: historical #
############################################################


def test_fails_with_no_name_in_historical_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'description': 'test'
        }
        Schema.validate_schema(method='historical', schema=schema)
    assert exc_info.value.args[0] == 'Required field "name" not found in historical schema.'


def test_fails_with_no_description_in_historical_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'name': 'test'
        }
        Schema.validate_schema(method='historical', schema=schema)
    assert exc_info.value.args[0] == 'Required field "description" not found in historical schema.'


def test_fails_with_less_argument_value_in_multiple_filters():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'name': 'test',
            'description': 'test',
            'filters': [
                {
                    'entity_sentiment': [0, 10]
                },
                {
                    'entity_sentiment': [0]
                }
            ]
        }
        Schema.validate_schema(method='historical', schema=schema)
    assert exc_info.value.args[0] == '"entity_sentiment" has wrong number or arguments.'


def test_fails_with_missing_field_in_select_function_in_historical_schema():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'name': 'test',
            "description": 'test',
            'select': [
                {
                    'alias': 'harvested_at'
                }
            ]
        }
        Schema.validate_schema(method='historical', schema=schema)
    assert exc_info.value.args[0] == 'Missing "field" in select option.'


def test_fails_alias_diff_function_for_harvested_at():
    with pytest.raises(error.SchemaError) as exc_info:
        schema = {
            'name': 'test',
            'description': 'test',
            'select': [
                {
                    'field': 'harvested_at',
                    'alias': 'hour',
                    'function': 'hourly'
                }
            ]
        }
        Schema.validate_schema(method='historical', schema=schema)
    assert exc_info.value.args[0] == "Alias of harvested_at is different from it's aggregation function."


def test_get_agg_function_for_missing_categorical_field():
    schema = {
        'name': 'test',
        'description': 'test',
        'select': [
            {
                'field': 'entity_ticker'
            },
            {
                'field': 'harvested_at',
                'alias': 'hour',
                'function': 'hour'
            }
        ]
    }
    schema = Schema.validate_schema(method='historical', schema=schema)
    assert schema['select'][0]['function'] == 'group'


def test_get_agg_function_for_missing_range_field():
    schema = {
        'name': 'test',
        'description': 'test',
        'select': [
            {
                'field': 'entity_sentiment'
            },
            {
                'field': 'harvested_at',
                'alias': 'hour',
                'function': 'hour'
            }
        ]
    }
    schema = Schema.validate_schema(method='historical', schema=schema)
    assert schema['select'][0]['function'] == 'average'
