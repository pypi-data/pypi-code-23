# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

import re
from operator import mul

from cached_property import cached_property

from ..group import Group, GroupItem


class HardwareItem(GroupItem):

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

    def iter_matching_port_speed(self, speed):
        match_value = dict(unit='G', value=speed)

        for panel in self['layout']:
            p_id = panel['panel_id']
            if panel['default_speed'] == match_value:
                yield (p_id, 'default', mul(*panel['panel_layout'].values()))

            for transf in panel['supported_transformations']:
                if transf['to_speed'] == match_value:
                    yield (p_id, 'to', transf['to_count'] - transf['from_count'] + 1)

    def matching_port_speed(self, speed):
        return list(self.iter_matching_port_speed(speed))

    def supports_port_speed(self, speed):
        match_value = dict(unit='G', value=speed)
        for panel in self['layout']:
            if panel['default_speed'] == match_value:
                return True
            for transf in panel['supported_transformations']:
                if transf['to_speed'] == match_value:
                    return True


class HardwareTypes(Group):
    group_endpoint = '/api/hcl'
    groupitem_class = HardwareItem
    groupitem_label = 'display_name'


def plugin(aos):
    return HardwareTypes(aos)
