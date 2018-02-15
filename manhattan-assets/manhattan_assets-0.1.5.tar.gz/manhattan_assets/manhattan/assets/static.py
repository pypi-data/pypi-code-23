"""
Functions for handling static assets.

The handling of static assets is likely to be project specific, however we
provide support for the default approach we use at getme on the basis that it's
simple to understand and deploy no matter you static asset pipeline.
"""

import json
import os


def get_static_asset(filepath):
    """
    Return a function for handling static assets.

    The returned function will look for a JSON file using the provided
    `filepath`. The JSON file (what we refer to as an asset pack) will contain
    a map of file references and their physical location, e.g:

        {'site.js': 'http://assets.mysite.co.uk/site.s3c8f6.js'}

    When the returned function is called (typically within a Jinja template) it
    will be passed a file reference and return the phsyical location.
    """

    # The date/time the asset pack was last modified
    last_modified = 0

    # A map of file references to physical locations
    file_map = {}

    # Only attempt to load the asset map on start up
    if os.path.exists(filepath):
        with open(filepath) as f:
            file_map = json.load(f)

    def _get_static_asset(file_ref):

        # Check if the asset is being served by a live server
        if '__live__' in file_map:
            return file_map['__live__'] + file_ref

        return file_map.get(file_ref, file_ref)

    return _get_static_asset