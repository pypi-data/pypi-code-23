import sys
import argparse
import signal
import base64
import abc
import ssl

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

import ldap3
import ldap3.core.exceptions
from ldap3.utils.dn import parse_dn


class CmdlineError(Exception):
    pass


def parse_comma_list(text):
    if text is None:
        return None
    return [s.strip().lower() for s in text.split(',')]


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""


class RequestHandler(BaseHTTPRequestHandler):
    backends = []
    config = None
    _log_user = '-'

    def log_message(self, format, *args):
        sys.stderr.write("%s - %s [%s] %s\n" %
                         (self.address_string(),
                          self._log_user,
                          self.log_date_time_string(),
                          format % args))

    @staticmethod
    def _parse_constraints(headers):
        return {
            'require_users': parse_comma_list(
                headers.get('AuthProxy-Require-Users')),
            'require_groups': parse_comma_list(
                headers.get('AuthProxy-Require-Groups'))
        }

    def _try_auth(self, auth_header):
        constraints = self._parse_constraints(self.headers)
        if (auth_header is not None
                and auth_header.lower().startswith('basic ')):
            creds = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = creds.split(':', 1)
            if constraints['require_users']:
                if username.lower() not in constraints['require_users']:
                    return False
            for backend in self.backends:
                if backend.authenticate(username, password, constraints):
                    self._log_user = username
                    return True

    def _auth_prompt(self):
        self.send_response(401)
        realm = self.headers.get('AuthProxy-Realm', 'Please login')
        self.send_header('WWW-Authenticate',
                         'Basic realm="{}"'.format(realm))
        self.send_header('Cache-Control', 'no-cache')

    def do_GET(self):
        try:
            auth_header = self.headers.get('Authorization')
            if (auth_header is None
                    or not auth_header.lower().startswith('basic ')):
                self._auth_prompt()
            authorized = self._try_auth(auth_header)
            if authorized:
                self.send_response(200)
            elif self.config.reauth:
                self._auth_prompt()
            else:
                self.send_response(403)
            self.end_headers()
        except Exception as e:
            eprint(str(e))
            self.send_response(500)
            self.end_headers()
            raise


class AuthBackend(abc.ABC):
    schemes = []

    def __init__(self, url, config):
        self.url = url
        self.config = config

    @abc.abstractmethod
    def authenticate(self, username, password, constraints):
        pass

    @classmethod
    def cmdline_args(cls, parser):
        pass


class LDAPAuthBackend(AuthBackend):
    schemes = ['ldap', 'ldaps', 'ldapi']

    def __init__(self, url, config):
        super(LDAPAuthBackend, self).__init__(url, config)
        if not config.ldap_user_pattern:
            raise CmdlineError('--ldap-user-pattern required!')

    @classmethod
    def cmdline_args(cls, parser):
        parser.add_argument('--ldap-user-pattern', dest='ldap_user_pattern',
                            metavar='',
                            help='User DN string with {} for username')
        parser.add_argument('--ldap-member-attr', default='memberOf',
                            dest='ldap_member_attr', metavar='',
                            help='User attribute containing group memberships')

    def _ldap_server(self):
        use_ssl = self.url.startswith('ldaps')
        tls = None
        if use_ssl:
            v = ssl.CERT_REQUIRED if self.config.verify else ssl.CERT_NONE
            tls = ldap3.Tls(validate=v,
                            ca_certs_file=self.config.ca_certs_file,
                            ca_certs_path=self.config.ca_certs_dir)
        return ldap3.Server(self.url, use_ssl=use_ssl, tls=tls)

    def authenticate(self, username, password, constraints):
        user_dn = self.config.ldap_user_pattern.format(username)
        try:
            conn = ldap3.Connection(self._ldap_server(), user_dn, password,
                                    auto_bind=True)
        except ldap3.core.exceptions.LDAPBindError:
            return False
        else:
            if constraints['require_groups']:
                attr = self.config.ldap_member_attr
                filter_, base = conn.user.split(',', 1)
                conn.search(base, '({})'.format(filter_), attributes=[attr])
                for membership in getattr(conn.entries[0], attr).values:
                    try:
                        rdns = parse_dn(membership)
                    except ldap3.core.exceptions.LDAPInvalidDnError:
                        group = membership
                    else:
                        group = rdns[0][1]
                    if group.lower() in constraints['require_groups']:
                        return True
            else:
                return True


AUTH_BACKENDS = [LDAPAuthBackend]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def exit_gracefully(signal, frame):
    sys.exit(0)


def arg_parser(backends):
    desc = 'Simple HTTP server to proxy authentication requests.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-b', '--bind', dest='bind', metavar='BIND',
                        help='IP:port to bind to (default: 127.0.0.1:8018)',
                        default='127.0.0.1:8018')
    parser.add_argument('-u', '--url', dest='urls', metavar='URL',
                        action='append', required=True,
                        help='URL of auth server (multiple, required)')
    parser.add_argument('-p', '--prompt', dest='reauth', action='store_true',
                        help='Return 401 when unauthorized')
    parser.add_argument('--ca-certs-file', dest='ca_certs_file', metavar='',
                        help='Path to CA certs bundle file')
    parser.add_argument('--ca-certs-dir', dest='ca_certs_dir', metavar='',
                        help='Path to directory containing CA certs')
    parser.add_argument('--no-verify', dest='verify', action='store_false',
                        help='Skip TLS verification')
    for backend in backends:
        backend.cmdline_args(parser)
    return parser


def main():
    parser = arg_parser(AUTH_BACKENDS)
    args = parser.parse_args()
    signal.signal(signal.SIGINT, exit_gracefully)

    backends = []
    try:
        for url in args.urls:
            scheme = url.partition('://')[0]
            scheme_handlers = [p(url, args) for p in AUTH_BACKENDS
                               if scheme in p.schemes]
            if not scheme_handlers:
                raise CmdlineError('Unknown scheme: {}'.format(scheme))
            backends.extend(scheme_handlers)
    except CmdlineError as e:
        eprint(str(e))
        return 1

    ip, port = args.bind.split(':')
    print('Listening on {}:{}'.format(ip, port))
    RequestHandler.backends = backends
    RequestHandler.config = args
    server = ThreadedHTTPServer((ip, int(port)), RequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    sys.exit(main())
