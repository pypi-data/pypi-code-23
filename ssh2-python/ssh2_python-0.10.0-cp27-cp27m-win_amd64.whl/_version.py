
import json

version_json = '''
{"date": "2018-02-14T12:17:54.851000", "full-revisionid": "7ddc3508f98a89f8943e4eca0a4f0950031aed29", "dirty": false, "version": "0.10.0", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

