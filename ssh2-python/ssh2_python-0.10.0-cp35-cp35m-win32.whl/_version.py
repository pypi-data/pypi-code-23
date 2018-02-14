
import json

version_json = '''
{"date": "2018-02-14T12:26:28.460121", "version": "0.10.0", "full-revisionid": "7ddc3508f98a89f8943e4eca0a4f0950031aed29", "error": null, "dirty": false}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

