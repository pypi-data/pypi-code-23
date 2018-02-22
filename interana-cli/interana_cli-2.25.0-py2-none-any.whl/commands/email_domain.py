# Copyright 2017 Interana, Inc.
'''
ia email-domain add
ia email-domain remove
ia email-domain list
'''

from base import CommandHandler, SubCommandHandler, DoResult
from ..utils.shared_parsers import add_output_parameters
import json


class EmailDomainHandler(CommandHandler):

    name = 'email-domain'
    description = 'Commands for managing email domains.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(AddEmailDomain(),
                                  RemoveEmailDomain(),
                                  ListEmailDomains())


class AddEmailDomain(SubCommandHandler):

    name = 'add'
    description = 'Add email domains for self-registration'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'email_domains',
            help='Email domains to add for self-registration. Can be a single value (i.e. "interana.com") or a '
            'comma separated list (i.e. "interana.com,ramneedle.com")',
            type=str
        )
        return parser

    def do(self):
        params = {
            'email_domains': self.args.email_domains
        }
        res = self.post('{hostname}/api/add_email_domain', data=params)
        return self._handle_basic_response(res)


class RemoveEmailDomain(SubCommandHandler):

    name = 'remove'
    description = 'Remove email domains from self-registration'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'email_domains',
            help='Email domains to remove from self-registration. Can be a single value (i.e. "interana.com") or a '
            'comma separated list (i.e. "interana.com,ramneedle.com")',
            type=str
        )
        return parser

    def do(self):
        params = {
            'email_domains': self.args.email_domains
        }
        res = self.post('{hostname}/api/remove_email_domain', data=params)
        return self._handle_basic_response(res)


class ListEmailDomains(SubCommandHandler):

    name = 'list'
    description = 'List email domains for registration'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        return parser

    def do(self):
        res = self.get('{hostname}/api/list_email_domains')
        email_domains_res = json.loads(res.content)['data']
        if not email_domains_res:
            return DoResult(message="No email-domains were found for this customer_id.")
        return DoResult(entries=[[email_domain] for email_domain in email_domains_res],
                        headers=['Email Domain'])
