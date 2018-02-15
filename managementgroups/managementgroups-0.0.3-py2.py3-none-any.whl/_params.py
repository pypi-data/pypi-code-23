# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands.parameters import get_three_state_flag

# pylint: disable=line-too-long


def load_arguments(self, _):
    with self.argument_context('account management-group show') as c:
        c.argument(
            'group_name',
            options_list=[
                '--group-name',
                '--name',
                '-n'])
        c.argument(
            'expand',
            arg_type=get_three_state_flag(),
            options_list=[
                '--expand',
                '-e'])
        c.argument(
            'recurse',
            arg_type=get_three_state_flag(),
            options_list=[
                '--recurse',
                '-r'])

    with self.argument_context('account management-group create') as c:
        c.argument('group_name', options_list=['--group-name', '--name', '-n'])
        c.argument('display_name', options_list=['--display-name', '-d'])
        c.argument('parent_id', options_list=['--parent-id', '-p'])

    with self.argument_context('account management-group update') as c:
        c.argument('group_name', options_list=['--group-name', '--name', '-n'])
        c.argument('display_name', options_list=['--display-name', '-d'])
        c.argument('parent_id', options_list=['--parent-id', '-p'])

    with self.argument_context('account management-group delete') as c:
        c.argument('group_name', options_list=['--group-name', '--name', '-n'])

    with self.argument_context('account management-group subscription add') as c:
        c.argument('group_name', options_list=['--group-name', '--name', '-n'])

    with self.argument_context('account management-group subscription remove') as c:
        c.argument('group_name', options_list=['--group-name', '--name', '-n'])
