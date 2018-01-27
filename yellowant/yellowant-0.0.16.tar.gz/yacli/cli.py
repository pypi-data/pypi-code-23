"""Entry point for the YellowAnt Developer CLI"""
import os
import sys
import ConfigParser
import click
import requests


CONTEXT_SETTINGS = dict(auto_envvar_prefix='yacli')


class Context(object):
    """YellowAnt Dev CLI common methods"""
    YELLOWANT_HOST = "https://yellowant.com"

    def __init__(self):
        self.verbose = False
        self.requests = None

        try:
            self.get_auth_from_config_file()
        except:
            self.token = None
            self.host = None
    
    def is_auth_valid(self):
        """Check if authentication credentials are present"""
        if self.token is None or self.host is None:
            raise click.ClickException("You cannot perform this command without authentication.\n" +\
                                       "Run 'yellowant auth' to remember authentication credentials, or provide '--token' and '--host' flag values before this command")
    
    def get_auth_from_config_file(self):
        """Load authentication credentials from config file"""
        # get home directory for UNIX or windows systems
        self.config_file = os.path.join((os.getenv("HOME") or os.getenv("HOMEPATH")), ".yellowant")
        config = ConfigParser.ConfigParser()
        config.read(self.config_file)
        self.token = config.get("YELLOWANT_DEV", "token")
        self.host = config.get("YELLOWANT_DEV", "host")
    
    def create_requests_object(self):
        """Add headers to requests object"""
        self.requests = requests.Session()
        self.requests.headers.update({
            "Authorization": "Token {}".format(self.token),
            "Content-type": "application/json"
        })
    
    def build_endpoint(self, endpoint):
        """Join the host, api, and enpoint"""
        if self.host[-1] == "/":
            # remove trailing slash
            self.host = self.host [:-1]
        return "".join([self.host, endpoint])
    
    def get(self, endpoint):
        """requests GET method wrapper"""
        self.create_requests_object()
        return self.requests.get(self.build_endpoint(endpoint))

    def post(self, endpoint, data=None):
        """requests POST method wrapper"""
        self.create_requests_object()
        return self.requests.post(self.build_endpoint(endpoint), data=data)

    def put(self, endpoint, data=None):
        """requests PUT method wrapper"""
        self.create_requests_object()
        return self.requests.put(self.build_endpoint(endpoint), data=data)

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)


pass_context = click.make_pass_decorator(Context, ensure=True)
CMD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__),'commands'))


class YellowAntDevCLI(click.MultiCommand):
    """Base Command"""
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(CMD_FOLDER):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('yacli.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


@click.command(cls=YellowAntDevCLI, context_settings=CONTEXT_SETTINGS)
@click.option("--token", help="YellowAnt Developer Token")
@click.option("--host", help="Yellowant Host URL")
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@pass_context
def cli(ctx, token=None, host=None, verbose=False):
    """This tool allows YellowAnt application developers to manage their applications."""
    ctx.verbose = verbose
    if token is not None:
        ctx.token = token
    if host is not None:
        ctx.host = host
