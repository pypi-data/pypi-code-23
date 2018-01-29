
import json

version_json = '''
{"dirty": false, "error": null, "version": "0.9.0", "full-revisionid": "923d4fe7cbc626d9203667a3e61634f160834552", "date": "2018-01-29T14:08:35.290989"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

