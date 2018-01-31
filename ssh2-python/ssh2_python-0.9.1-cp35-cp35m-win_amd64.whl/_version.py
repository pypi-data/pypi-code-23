
import json

version_json = '''
{"date": "2018-01-31T20:02:50.595450", "error": null, "dirty": false, "version": "0.9.1", "full-revisionid": "06db8a485613efd619d530e61a5513a49c6abe9a"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

