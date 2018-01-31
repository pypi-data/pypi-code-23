
import json

version_json = '''
{"date": "2018-01-31T20:09:34.621297", "dirty": false, "error": null, "full-revisionid": "06db8a485613efd619d530e61a5513a49c6abe9a", "version": "0.9.1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

