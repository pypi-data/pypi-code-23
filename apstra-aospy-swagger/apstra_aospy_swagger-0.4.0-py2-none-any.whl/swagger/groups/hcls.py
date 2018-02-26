# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

import re
from cached_property import cached_property
from aospy.swagger.indexer import Indexer, IndexItem


class HardwareItem(IndexItem):
    @cached_property
    def os_version_re(self):
        return re.compile(self.value['selector']['os_version'])

    @property
    def os(self):
        return self.value['selector']['os']

    @property
    def model(self):
        return self.value['selector']['model']

    @property
    def vendor(self):
        return self.value['selector']['manufacturer']

    def version_matches(self, version):
        return bool(self.os_version_re.match(version))


class HardwareList(Indexer):
    def __init__(self, aos):
        rqst = aos.request.hcl.get_hcls
        super(HardwareList, self).__init__(rqst, index_item_type=HardwareItem)
        self.run()
