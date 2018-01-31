
import json

version_json = '''
{"full-revisionid": "06db8a485613efd619d530e61a5513a49c6abe9a", "dirty": false, "date": "2018-01-31T19:49:01.374179", "error": null, "version": "0.9.1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

