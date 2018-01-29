
import json

version_json = '''
{"date": "2018-01-29T14:03:42.220000", "full-revisionid": "923d4fe7cbc626d9203667a3e61634f160834552", "dirty": false, "version": "0.9.0", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

