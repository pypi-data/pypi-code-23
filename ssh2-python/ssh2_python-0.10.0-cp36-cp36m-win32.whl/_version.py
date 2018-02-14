
import json

version_json = '''
{"date": "2018-02-14T12:39:27.728079", "dirty": false, "error": null, "full-revisionid": "7ddc3508f98a89f8943e4eca0a4f0950031aed29", "version": "0.10.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

