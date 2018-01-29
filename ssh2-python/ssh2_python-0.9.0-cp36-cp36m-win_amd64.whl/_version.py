
import json

version_json = '''
{"date": "2018-01-29T14:29:37.968762", "dirty": false, "error": null, "full-revisionid": "923d4fe7cbc626d9203667a3e61634f160834552", "version": "0.9.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

