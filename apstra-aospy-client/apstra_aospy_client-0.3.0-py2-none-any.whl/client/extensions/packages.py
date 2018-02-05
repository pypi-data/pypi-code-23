# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

from os import path
from ..group import Group


class Packages(Group):
    group_endpoint = '/api/packages'
    groupitem_label = 'name'
    groupitem_id = 'name'

    def upload(self, uploadfile):
        with open(uploadfile) as pkg_file:
            packagename = path.basename(pkg_file.name)
            url = "%s?packagename=%s" % (self.url, packagename)

            got = self.api.post(url, data=pkg_file.read())
            if not got.ok:
                raise RuntimeError("ERROR: %s install failed: %s" % got.reason)

        # automatically reload the catalog
        self.fetch_items()


def plugin(aos):
    return Packages(aos)
