
import json

version_json = '''
{"version": "0.10.0", "full-revisionid": "7ddc3508f98a89f8943e4eca0a4f0950031aed29", "error": null, "date": "2018-02-14T12:19:39.404389", "dirty": false}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

