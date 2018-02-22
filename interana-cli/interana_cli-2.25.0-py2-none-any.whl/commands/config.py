# Copyright 2017 Interana, Inc.
from base import CommandHandler
from getpass import getpass
from ..utils import config
from ..utils.shared_parsers import add_unsafe_ssl, add_custom_help, add_verbose_errors


class ConfigHandler(CommandHandler):

    name = 'config'
    description = 'Configure credentials for this tool.'

    def __init__(self):
        CommandHandler.__init__(self)

    def parser_setup(self, sps):
        parser = sps.add_parser(self.name, help=self.description, add_help=False)
        parser.set_defaults(command=self.name)
        add_custom_help(parser)

        g = parser.add_argument_group("Generic")
        add_verbose_errors(g)
        add_unsafe_ssl(g)

        parser.add_argument(
            'url',
            help='https URL with FQDN of the instance',
            type=str
        )

        parser.add_argument(
            '--instance-name',
            help='Name assigned to instance, providing this allows you to authenticate to multiple clusters.',
            metavar='handle',
            type=str,
            default='default'
        )

    def do(self):
        self.hostname = self.args.url
        handle = self.args.instance_name

        version_url = '{hostname}'
        res = self.get(version_url, authenticated=False)

        if res.status_code != 200:
            print res
            raise Exception("Could not ping URL %s. Please make sure you typed the correct address." % version_url)

        print "Visit {url}/api/create_token and supply your new API token.".format(url=self.hostname)
        self.api_token = getpass('Enter API Token: ').strip()

        headers = {}
        headers['Authorization'] = 'Token ' + self.api_token
        res = self.get('{hostname}/api/version/get', headers=headers, authenticated=False)
        if res.status_code != 200:
            raise Exception("API Token Invalid")

        config.write_rcconfig(self.hostname, self.api_token, handle)

        print "Success! Credentials stored as {0} config".format(handle)
