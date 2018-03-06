import argparse
import bottle
from cheroot import wsgi
from cheroot.ssl.builtin import BuiltinSSLAdapter
import json
import os
import socket
import ssl
import sys
import threading

from . import execEnv
from . import basics
from . import utilities

###############################################################################################
# constants
###############################################################################################


# this file is generated in the folder in which this __file__ is stored when it is executed.
# It is supposed to be temporary and should not be uploaded to anywhere.
# It is listed as excluded in MANIFEST.in of this pip installer
# and also the Django command uploadCoreLibraries deletes it before the upload, just to be safe.
_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CONFIG.txt')
_config = None
def _get_config():
    """
    load constants from a configuration file.
    Uses a cache.
    """
    global _config
    if _config is None:
        with open(_CONFIG_FILE, 'r') as f:
            _config = json.load(f)
    return _config

def _get_server_url():
    """
    get a connection string that can be used to connect to the server
    """
    use_local_server = _get_config()['use_local_server']
    if use_local_server:
        url = basics.get_shared_truth()['debug_server_url']
    else:
        url = basics.get_shared_truth()['server_url']
    return url

def _get_json_encoding_of_server():
    """
    get the type of encoding that the server uses for encoding JSON strings
    """
    res = basics.get_shared_truth()['json_encoding']
    return res


##############################################################################################################
# main - initialize
##############################################################################################################


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


##############################################################################################################
# helper functions for authorization
##############################################################################################################


def require_collab_authentication(subparser):
    subparser.add_argument('-e', '--email', default=None,
        help="the password of your LOD account. This can be skipped if you have already used the 'configure' command.")
    subparser.add_argument('-p', '--password', default=None,
        help="the password of your LOD account. This can be skipped if you have already used the 'configure' command.")

def check_if_collab_credentials_are_configured(args):
    """
    if the arguments contain an email and password, return them.
    If not, check if there is a configuration file and use it.
    """
    if args.email is not None and args.password is not None:
        return
    l = [args.email, args.password]
    if not all(v is None for v in l) and not all(v is not None for v in l):
        raise ValueError("either both or neither of email and password must be specified.")
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            args.email = config['email']
            args.password = config['password']
    else:
        raise ValueError("email and password for Collab must be specified. Either use a configuration file for this or provide them as arguments. See --help for details.")


##############################################################################################################
# main - functions
##############################################################################################################


def configure(args):
    with open(_CONFIG_FILE, 'w') as f:
        config = {
            'email' : args.email,
            'password' : args.password,
            'ssl_crt' : args.ssl_crt,
            'ssl_key' : args.ssl_key,
            'exec_env_root_folder' : args.exec_env_root_folder,
            'local_exec_env_port' : int(args.local_exec_env_port),
            'debug_mode' : args.debug_mode,
            'serverside_exec_env_recognition_key' : args.serverside_exec_env_recognition_key,
        }
        if args.use_debug_server:
            # if this is running with the debugging server, use the debugging server's url
            config['server_contact_url'] = basics.get_shared_truth()['debug_server_url']
        else:
            config['server_contact_url'] = basics.get_shared_truth()['server_url']
        json.dump(config, f)
    print("successfully created configuration file.")

subparser = subparsers.add_parser('configure',
    help="""creates a configuration file to store your login credentials, so you don't have to specify them every time.
    Be aware that anyone who steals this configuration file will be able to log in with your credentials unless you delete the file again.""")
subparser.add_argument('-e', '--email', required=True,
    help="the email of your LOD account.")
subparser.add_argument('-p', '--password', required=True,
    help="the password of your LOD account.")
subparser.add_argument('--ssl-crt', required=True,
    help="""the location of a certificate file on your machine that is trusted by your browser.
    If this doesn't exist, you can use the 'create-certificate' command to create it later.""")
subparser.add_argument('--ssl-key', required=True,
    help="""the location of the key file corresponding to the certificate file for --ssl-crt.
    If this doesn't exist, you can use the 'create-certificate' command to create it later.""")
subparser.add_argument('-r', '--exec-env-root-folder', required=True,
    help="""the path to the root folder in which files will be created when the Scenario runs.""")
subparser.add_argument('-port', '--local_exec_env_port', required=True,
    help="the port on which the ExecEnv will listen to incoming requests.")
# connect to a locally running test server instead of the real server
subparser.add_argument('--use-debug-server', action='store_true',
    help=argparse.SUPPRESS)
# run in debug mode
subparser.add_argument('--debug-mode', action='store_true',
    help=argparse.SUPPRESS)
# a masterkey used only on the server. This is used instead of the user and password.
subparser.add_argument('-key', '--serverside_exec_env_recognition_key', required=False, default=None,
    help=argparse.SUPPRESS)
subparser.set_defaults(func=configure)


def delete_configuration(args):
    if os.path.isfile(_CONFIG_FILE):
        os.remove(_CONFIG_FILE)
        return
    else:
        raise ValueError("no config file exists.")

subparser = subparsers.add_parser('delete-configuration',
    help="""deletes the configuration file that stores your login credentials.""")
subparser.set_defaults(func=delete_configuration)


def create_self_signed_cert(args):
    """
    create a new self-signed SSL certificate.
    """
    # get the configuration of the certificate
    # (note: this is a copy of /System/Library/OpenSSL/openssl.cnf, which is put here because )
    certificate_configuration_file_basis = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'copy_of_openssl.cnf')
    with open(certificate_configuration_file_basis, 'r') as f:
        certificate_configuration = f.read()
        certificate_configuration += "[SAN]\nsubjectAltName=DNS:localhost'"
    # temporarily alter the certificate_configuration
    # (note that this file will be deleted at the end of this function, and that it is marked to be excluded by pip)
    certificate_configuration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TMP_certificate_configuration.txt')
    try:
        with open(certificate_configuration_file, 'w') as f:
            f.write(certificate_configuration)
        # make the command for OpenSSL
        cmd = [
            'openssl',
            'req',
            '-newkey', 'rsa:2048',
            '-x509',
            '-nodes',
            '-keyout', _get_config()['ssl_key'],
            '-new',
            '-out', _get_config()['ssl_crt'],
            '-subj', '/CN=lod-executor (LegionOfDevs)',
            '-reqexts', 'SAN',
            '-extensions', 'SAN',
            '-config', certificate_configuration_file,
            '-sha256',
            '-days', '3650',
        ]
        # create the certificate
        utilities.execute_terminal_command(cmd)
    finally:
        # delete the certificate_configuration file
        os.remove(certificate_configuration_file)
    print("Successfully created a certificate.")
    print("Make sure that the certificate file (%s) is trusted by your browser for SSL connections." % (_get_config()['ssl_crt'],))
    print("Then, with this program running with the 'run' command, verify that you can reach the following website with your browser:")
    print("https://localhost:%s/certificate_test" % (_get_config()['local_exec_env_port'],))

subparser = subparsers.add_parser('create-certificate',
    help="""Creates a self-signed certificate in the location specified by your configuration.
    Use this if you don't already have a certificate for localhost.
    Note: after calling this function you may still need to configure your machine to accept the created certificate.""")
subparser.set_defaults(func=create_self_signed_cert)


def delete_files_of_executions(args):
    if os.path.isfile(_CONFIG_FILE):
        exec_env_root_folder = _get_config()['exec_env_root_folder']
        for f in os.listdir(exec_env_root_folder):
            path = os.path.join(exec_env_root_folder, f)
            utilities.delete_file_or_folder(path)
        return
    else:
        raise ValueError("no config file exists.")

subparser = subparsers.add_parser('clean',
    help="""deletes the content of the folder that was specified as the exec_env_root_folder during configuration.
    This deletes all files that were generated while executing Scenarios.""")
subparser.set_defaults(func=delete_files_of_executions)


def run_in_loop(args):
    check_if_collab_credentials_are_configured(args)
    # create the ExecEnvManager
    execEnv.initialize_execution_environment_manager(_get_config(), basics.get_shared_truth(), args)
    # close ExecEnvs that have no incoming requests for too long (this happens if the Scenario has been closed but not properly shut down by the user)
    # (this function starts a regular check for idle ExecEnvs)
    _shut_down_idle_exec_envs()
    # start listening for incoming messages
    port_to_listen_to = _get_config()['local_exec_env_port']
    print("listening on port %s..." % (port_to_listen_to,))
    bottle_is_quiet = (not args.verbose)
    try:
        # note: host='localhost' ensures that this can ony be accessed from the localhost
        bottle.run(host='localhost', port=port_to_listen_to, server=SSLCherryPyServer, quiet=bottle_is_quiet)
    except (KeyboardInterrupt, SystemExit):
        print('keyboard interrupt')


subparser = subparsers.add_parser('run', help="Starts running the ExecEnv so that the website can connect to it.")
subparser.add_argument('-v', '--verbose', action='store_true',
    help="print additional information to the console.")
require_collab_authentication(subparser)
subparser.set_defaults(func=run_in_loop)


##############################################################################################################
# make the server use an SSL certificate, so that https works with localhost connections
##############################################################################################################


@bottle.route('/certificate_test')
def hello():
    return "Success!\nIf you are reading this, your browser accepts the SSL connection."


class SSLCherryPyServer(bottle.ServerAdapter):
    """
    Create our own sub-class of Bottle's ServerAdapter
    so that we can specify SSL. Using just server='cherrypy'
    uses the default cherrypy server, which doesn't use SSL
    """
    def run(self, handler):
        server = wsgi.Server((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter(_get_config()['ssl_crt'], _get_config()['ssl_key'], None)
        # By default, the server will allow negotiations with extremely old protocols
        # that are susceptible to attacks, so we only allow TLSv1.2
        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1
        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1_1
        try:
            server.start()
        finally:
            server.stop()


##############################################################################################################
# code for the server that listens for requests
##############################################################################################################


@bottle.route('/', method='POST')
def main_server_input():
    request_data = bottle.request.forms['request_data']
    request_data = json.loads(request_data)
    try:
        response_data = execEnv._the_manager.process_message_from_scenario(request_data)
    except:
        error_message = utilities.get_error_message_details()
        error_message = "Exception during processing of command:\n%s" % (error_message,)
        print(error_message)
        response_data = {
            'success' : False,
            'error_message' : error_message,
        }
    return(json.dumps(response_data))


@bottle.hook('after_request')
def enable_cors():
    """
    add some headers to each request.
    """
    # tell any requests from server_contact_url that they are ok
    the_server_url = _get_config()['server_contact_url']
    if the_server_url.endswith('/'):
        the_server_url = the_server_url[:-1]
    bottle.response.headers['Access-Control-Allow-Origin'] = the_server_url
    bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


##############################################################################################################
# shutting down idle ExecEnvs
##############################################################################################################


def _shut_down_idle_exec_envs():
    """
    close ExecEnvs that have no incoming requests for too long (this happens if the Scenario has been closed but not properly shut down by the user)
    This function restarts itself so that it is called every few seconds.
    """
    # start this function again in a few seconds
    t = threading.Timer(5.0, _shut_down_idle_exec_envs)
    t.daemon = True # this needs to be a Daemon so that KeyboardInterrupt works
    t.start()
    # shut down all idle ExecEnvs
    execEnv._the_manager.shut_down_idle_exec_envs()


##############################################################################################################
# shutting down everything when the program is shut down
##############################################################################################################


import atexit
def exit_handler():
    if execEnv._the_manager is not None:
        execEnv._the_manager.shut_down_and_wait()
atexit.register(exit_handler)


##############################################################################################################
# main - finalize
##############################################################################################################


def main():
    if len(sys.argv)==1:
        # if the program is called without arguments, print the help menu and exit
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args()
        args.func(args)

if __name__ == '__main__':
    main()
