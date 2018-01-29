
import json

version_json = '''
{"date": "2018-01-29T14:17:25.683461", "dirty": false, "version": "0.9.0", "full-revisionid": "923d4fe7cbc626d9203667a3e61634f160834552", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

