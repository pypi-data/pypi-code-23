"""Utility functions to simplify common cloud bundle operations"""
import atexit
import json
from tempfile import mkstemp

import os


def create_transient_file(file_contents):
    """Creates a temporary file that will be automatically removed after program exits

    Useful for pushing credential files from Swimlane context to disk for authentication

    Returns path to new temporary file
    """

    # Create and write to temp file
    tmp_file_path = mkstemp()[1]
    with open(tmp_file_path, 'wb') as f:
        f.write(file_contents)

    # Cleanup temp file at shutdown
    atexit.register(lambda: os.remove(tmp_file_path))

    return tmp_file_path


class _IgnoreInvalidEncoder(json.JSONEncoder):
    """JSON encoder defaulting to stringifying any objects not supporting default JSON serialization"""
    def default(self, o):
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)


def safe_json_dumps(target):
    """Safely dump JSON, default to stringifying anything not serializable by default"""
    return json.dumps(
        target.get('extra', {}),
        indent=4,
        cls=_IgnoreInvalidEncoder
    )
