
import json

version_json = '''
{"full-revisionid": "06db8a485613efd619d530e61a5513a49c6abe9a", "dirty": false, "error": null, "date": "2018-01-31T19:52:19.789199", "version": "0.9.1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

