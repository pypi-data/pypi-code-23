import os.path

OPENAPI21_PATH = os.path.dirname(os.path.realpath(__file__))
SCHEMA_URL = 'file:{}/spec/schema.json'.format(OPENAPI21_PATH)

from openapi21.validator import (validate_spec_url,
                                 validate_spec,
                                 validate_json)
