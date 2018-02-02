
# The SSH client that sends message to the remote server.

import logging, os, re, sys, functools, socket
import paramiko
from os.path import join, abspath, dirname

from .protocol import encode, read_msg, ProtocolError

logger = logging.getLogger('pepperssh')


def _disable_logging():
    # I'm not sure how Python logging is supposed to work.  The paramiko library logs to
    # *info*.  I guess they expect that you always only log warnings in production?
    #
    # If it doesn't look like logging was specifically set for paramiko, change it to
    # warning instead of info.
    l = logging.getLogger('paramiko')
    if l.level == 0:
        l.setLevel(logging.WARNING)


class ClientConnection:
    def __init__(self, host):
        _disable_logging()

        self.host = host
        self.sshclient = None

        self.rpath = None
        # The temporary library directory on the remote server.  Our package has been copied
        # into this directory, so the directory should be added to the system path.

        self.channel = None
        # The open channel we use to send commands and read responses.

    def connect(self):
        self.sshclient = paramiko.SSHClient()
        self.sshclient._policy = paramiko.WarningPolicy()
        self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        cfg = self.get_host_config()
        logger.debug('self.sshclient config: %r', cfg)

        self.sshclient.connect(**cfg)

        self._copypackage()
        self._bootstrap()

    def close(self):
        if self.sshclient:
            try:
                self.sshclient.close()
            except:
                pass
        self.sshclient = None
        self.channel = None

    def _copypackage(self):
        """
        Called during connect to copy the files necessary to bootstrap our
        server on the remote box.
        """
        # Copy our package to a temporary directory to be imported.
        #
        # Since all of our files are in the same directory we'll simply enumerate them and copy
        # them.

        rin, rout, rerr = self.sshclient.exec_command("python3.6 -c 'import tempfile; print(tempfile.mkdtemp())'")
        rpath = rout.read().strip().decode('utf-8')
        logger.debug('remote path=%s', rpath)

        sftp = self.sshclient.open_sftp()
        sftp.chdir(rpath)

        # Make the work directory world readable for now.  If the user is changed via sudo, we
        # want it to be able to read the files.
        #
        # TODO: Redesign the security aspects.  Perhaps we should make an easy way to change
        # the ownership, either in remote_file, or on the remote side.

        sftp.chmod(rpath, 0o777)

        # Create the directory where we'll put files we copy.

        sftp.mkdir('files')

        sftp.mkdir('pepperssh')
        lpath = dirname(abspath(__file__))
        for filename in os.listdir(lpath):
            lname = join(lpath, filename)
            if not lname.endswith('.py'):
                continue
            rname = join(rpath, 'pepperssh', filename)
            logger.debug('copying %s --> %s', lname, rname)
            sftp.put(lname, rname)

        sftp.close()

        self.sshclient = self.sshclient
        self.rpath     = rpath

    def _bootstrap(self):
        """
        Called during connect to start the Python server code that will listen
        for messages.
        """
        tran = self.sshclient.get_transport()
        self.channel = tran.open_session()
        self.channel.set_combine_stderr(True)

        # WARNING: Do *not* use self.channel.get_pty().  It causes stdin to be echoed to
        # stdout, so everything we send comes right back, followed by the response.

        # Note the "-u" for unbuffered output.

        cmd = """
              python3.6 -uc
              'import sys;
               sys.path.insert(0, "%s");
               from pepperssh import server;
               server.main()'
              """ % self.rpath
        cmd = re.sub(r'\s*[\n]\s*', ' ', cmd).strip()
        logger.debug('cmd: %s', cmd)
        self.channel.exec_command(cmd)

    def send_command(self, msg, *, timeout):
        """
        Sends a message (a dict) and waits for the response (also a dict).
        """
        logger.debug('send: %r', msg)
        header, msgout = encode(msg)
        self.channel.sendall(header)
        self.channel.sendall(msgout)

        result = self._read_response(timeout=timeout)

        if 'stdout' in result:
            stdout = result['stdout'].strip()
            if stdout:
                print(stdout)

        if result['msgtype'] == 'error':
            errormsg = ['An error occurred on the server']
            if 'error' in result:
                errormsg[0] += ': ' + result['error']
            if 'traceback' in result:
                errormsg.append(result['traceback'])

            sys.exit('An error occurred on the server: ' + '\n'.join(errormsg))

        return result

    def _read_response(self, *, timeout):
        """
        Returns the decoded response as a dictionary.
        """
        self.channel.settimeout(timeout)
        try:
            return read_msg(functools.partial(self.channel.recv, 50 * 1024))
        except ProtocolError as ex:
            # We tried to decode the header but the data isn't one of our messages.  This
            # usually means that (1) and exception occurred before we setup comms or (2) an
            # external utility printed to stderr without it being redirected.  Either way,
            # assume it was a failure and that the buffer contains an error message / trace.

            # Something is writing one line at a time, so we if we can get more.
            self.channel.settimeout(0.5)
            buffer = ex.data
            try:
                while 1:
                    data = self.channel.recv(50 * 1024)
                    if not data:
                        break
                    buffer += data
            except socket.timeout:
                pass

            try:
                buffer = buffer.decode('utf-8')
            except UnicodeDecodeError:
                pass

            logger.error('Unexpected data on the wire: %r', buffer)
            return {
                'msgtype': 'error',
                'error': buffer
            }

        finally:
            self.channel.settimeout(None)

    def get_host_config(self):
        cfg = {}
        cfg['hostname'] = self.host

        fqn = os.path.expanduser('~/.ssh/config')
        if os.path.exists(fqn):
            f = open(fqn)
            sc = paramiko.SSHConfig()
            sc.parse(f)

            hostconfig = sc.lookup(self.host)
            if hostconfig:
                for fromkey, tokey in CONFIGMAP.items():
                    if fromkey in hostconfig:
                        cfg[tokey] = hostconfig[fromkey]

            if 'key_filename' in cfg:
                cfg['key_filename'] = cfg['key_filename'][0]

        return cfg


CONFIGMAP = {
    # Maps from lowercased keywords in an OpenSSH config file to paramiko SSHClient
    # parameter names.
    'identityfile': 'key_filename',
    'user': 'username',
    'port': 'port'
}
