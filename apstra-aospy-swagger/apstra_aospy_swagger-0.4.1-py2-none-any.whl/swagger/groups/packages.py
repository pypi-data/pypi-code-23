# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

from os import path
from aospy.swagger.indexer import Indexer


class Packages(Indexer):

    def __init__(self, aos):
        super(Packages, self).__init__(
            rqst=aos.request.packages.get_api_packages,
            name_from='name', id_from='name')
        self.run()

    def upload(self, uploadfile):
        r_cl = self.rqst.client
        api = r_cl.remote.api
        url = r_cl.server_url + self.rqst.path

        with open(uploadfile) as pkg_file:
            packagename = path.basename(pkg_file.name)
            got = api.post(url + "?packagename=%s" % packagename,
                           data=pkg_file.read())
            if not got.ok:
                raise RuntimeError("ERROR: %s install failed: %s" % got.reason)

        # automatically reload the catalog
        self.run()
