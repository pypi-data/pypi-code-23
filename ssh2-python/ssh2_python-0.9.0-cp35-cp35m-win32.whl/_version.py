
import json

version_json = '''
{"full-revisionid": "923d4fe7cbc626d9203667a3e61634f160834552", "dirty": false, "date": "2018-01-29T14:12:11.944201", "error": null, "version": "0.9.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

