import paramiko
import atexit
from collections import namedtuple
from actappliance.connections.connection import ApplianceConnection


ssh_out = namedtuple('ssh_output', ['out', 'err', 'status'])


class ApplianceSsh(ApplianceConnection):
    def __init__(self, *args, **kwargs):
        super(ApplianceSsh, self).__init__(*args, **kwargs)

        # SSH delimiter to use during uds commands
        self.SSH_DELIM = '|MiLeD|'

        # set in method 'connect'
        self.ssh_client = None

    def connect(self):
        """
        Connect to an appliance, disable timeouts and return the ssh object.
        :return: paramiko ssh object
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.system, **self.connect_kwargs)
        except paramiko.SSHException:
            self.logger.exception("Failed to connect to {}".format(self.system))
            raise
        _, out, _ = ssh.exec_command("unset TMOUT")
        rc = out.channel.recv_exit_status()
        if rc != 0:
            raise RuntimeError("Return code of 'unset TMOUT was {}.".format(rc))
        self.ssh_client = ssh

        # Close this connection after execution
        atexit.register(self.disconnect)

    def disconnect(self):
        try:
            self.ssh_client.close()
        except (AttributeError, NameError):
            self.logger.debug("No ssh client to close.")
        self.ssh_client = None

    def _auto_connect(self):
        """
        :return: ActCmd object with ssh_command attribute
        """
        if not self.ssh_client:
            self.connect()

    def _get_ssh_out_from_command(self, exec_args=None, exec_kwargs=None, strip_newlines=False):
        exec_args = [] if exec_args is None else exec_args
        exec_kwargs = {} if exec_kwargs is None else exec_kwargs

        stdin_chan, stdout_chan, stderr_chan = self.ssh_client.exec_command(*exec_args, **exec_kwargs)
        stdin_chan.close()

        # Wait for exit_status
        exit_status = stdout_chan.channel.recv_exit_status()

        # get output from channelfiles
        stdout = stdout_chan.readlines()
        stderr = stderr_chan.readlines()
        if strip_newlines:
            stdout = [line.rstrip('\n') for line in stdout]
            stderr = [line.rstrip('\n') for line in stderr]
        self.logger.debug('stderr: \n{}'.format(stderr))
        self.logger.debug("exit status: {}".format(exit_status))
        return ssh_out(out=stdout, err=stderr, status=exit_status)

    def call(self, act_cmd):
        """
        Use when you explicitly want to connect over ssh and send raw ssh commands.

        This houses the functionality unlike rest method because I want to avoid passing around the client to retain
        channels.

        :param act_cmd: Instance of ActCmd object
        :return: stdout, stderr, exit status
        """
        super(ApplianceSsh, self).call(act_cmd)

        ssh_o = self._get_ssh_out_from_command(exec_kwargs=act_cmd.input.ssh_kwargs, strip_newlines=True)

        act_cmd.output.sshout = ssh_o

    def raw(self, ssh_command, statuses=None):
        """
        Send an ssh command with the only processing being newline stripping.

        Threaded timeouts still apply to `raw`. If you need absolute individual control use method `call`.

        :param ssh_command: command to send
        :param statuses: list of acceptable exit statuses
        :return: namedtuple ssh_output
        """
        self._auto_connect()

        ssh_o = self._get_ssh_out_from_command(exec_args=[ssh_command], strip_newlines=True)

        if statuses and ssh_o.status not in statuses:
            self.logger.debug("Failed stdout:\n{}\nFailed stderr:\n{}".format(ssh_o.out, ssh_o.err))
            raise RuntimeError("Exit status of command {} was {}; only {} accepted.".format(
                ssh_command, ssh_o.status, ','.join(str(s) for s in statuses))
            )

        return ssh_o
