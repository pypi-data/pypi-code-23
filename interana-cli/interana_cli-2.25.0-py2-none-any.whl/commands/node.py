# Copyright 2017 Interana, Inc.
'''
ia node add
ia node remove
ia node list
'''

from base import CommandHandler, SubCommandHandler
from interana.utils.shared_parsers import add_output_parameters, add_run_mode
import json


class NodeHandler(CommandHandler):

    name = 'node'
    description = 'Commands for managing cluster topology.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(AddNode(),
                                  RemoveNode(),
                                  ListNodes())


class AddNode(SubCommandHandler):
    name = 'add'
    description = 'Add nodes to cluster. Assuming nodes already exist and has interana installed on them.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
                'add_node',
                help='Node tier, public and private ip to be added to the cluster. '
                     'Should be in <tier:public_ip:private_ip> format. '
                     '(i.e. data:10.0.0.9:10.0.0.9 or '
                     'data:10.0.0.9:10.0.0.9, data:10.0.0.10:10.0.0.10)',
                nargs='+',
                metavar=('tier:public_ip:private_ip'),
                )
        return parser

    def do(self):
        params = {
            'nodes': json.dumps(self.args.add_node)
        }
        res = self.post('{hostname}/api/add_node', data=params)
        return self._handle_basic_response(res)


class ListNodes(SubCommandHandler):
    name = 'list'
    description = 'List nodes of the cluster.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        return parser

    def do(self):
        res = self.get('{hostname}/api/list_nodes')
        return self._handle_basic_response(res)


class RemoveNode(SubCommandHandler):
    name = 'remove'
    description = 'Remove nodes from the cluster.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
                'remove_node',
                help='Node uid to be deleted from the cluster. ',
                nargs='+',
                metavar=('uid')
                )
        add_run_mode(parser)
        return parser

    def do(self):
        params = {
            'nodes': json.dumps(self.args.remove_node),
            'run': self.args.run
        }
        res = self.post('{hostname}/api/remove_node', data=params)
        if not self.args.run:
            print "This is the preview mode; use --run/-r to execute removal."
        return self._handle_basic_response(res)
