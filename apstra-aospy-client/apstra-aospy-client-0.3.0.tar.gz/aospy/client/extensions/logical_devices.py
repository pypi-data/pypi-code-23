# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula


from ..group import Group


class LogicalDeviceTypes(Group):
    group_endpoint = '/api/design/logical-devices'
    groupitem_label = 'display_name'


def plugin(aos):
    return LogicalDeviceTypes(aos)
