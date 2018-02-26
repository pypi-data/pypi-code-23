import os
import hashlib

from subprocess import Popen, PIPE

from .mixins import CLHMixin
from .exceptions import PopenError


# region Helpers
class PopenHelper(CLHMixin):
    @staticmethod
    def execute_command(command):
        p = Popen(['/bin/bash',
                   '-eo',
                   'pipefail',
                   '-c',
                   command], stdout=PIPE, stderr=PIPE, close_fds=False)

        stdout, stderr = p.communicate()

        if p.returncode != 0:
            raise PopenError('Command failed: {errormsg}'.format(errormsg=stderr.rstrip('\n')))

        return p.returncode, stdout, stderr


class SshHelper(CLHMixin):
    DEFAULT_CONF = dict(
        ssh_pipelining=False,
        control_persist=1800,
        gzip_upload=True,
        strict_hostkey_checking=False,
        user_known_hosts_file='/dev/null'
    )

    _ssh_opts = str()

    @property
    def ssh_opts(self):
        return self._ssh_opts

    def __init__(self, hostname, *args, **kwargs):
        super(SshHelper, self).__init__(*args, **kwargs)
        self._hostname = hostname
        self._ph = PopenHelper(conf=self.rconf, logger=self.logger)

        if not self.conf.strict_hostkey_checking:
            self._ssh_opts += '-o StrictHostKeyChecking=no '

        self._ssh_opts += '-o UserKnownHostsFile={filename} '.format(
                            filename=self.conf.user_known_hosts_file)

        if self.conf.ssh_pipelining:
            md5 = hashlib.md5()
            md5.update(self._hostname)

            self._ssh_opts += '-oControlMaster=auto ' \
                              '-oControlPersist={control_persist} ' \
                              "-oControlPath='/tmp/ssh-mux-{hhash}%r%p' ".format(
                                  control_persist=self.conf.control_persist,
                                  hhash=md5.hexdigest()
                              )

    def execute_command(self, command):
        return self._ph.execute_command('ssh '
                                        '{ssh_opts} '
                                        "{host} '{command}'".format(
                                                        ssh_opts=self._ssh_opts,
                                                        host=self._hostname,
                                                        command=command
                                        ))

    def putc(self, command, remote_path, gzip=None, gunzip=None):
        if gzip is None and gunzip is None:
            gzip = gunzip = self.conf.gzip_upload

        return self._ph.execute_command('{command} | {gzip_command}'
                                        'ssh {host} '
                                        '{ssh_opts} '
                                        "'{cat_command} > {remote_path}'".format(
                                                            ssh_opts=self._ssh_opts,
                                                            command=command,
                                                            gzip_command='gzip --best |' if gzip else '',
                                                            host=self._hostname,
                                                            remote_path=remote_path,
                                                            cat_command='zcat' if gunzip else 'cat'
                                        ))

    def put(self, path, remote_path, gzip=None, gunzip=None):
        if gzip is None and gunzip is None:
            gzip = gunzip = self.conf.gzip_upload

        if gzip or gunzip:
            return self.putc('cat {path}'.format(path=path), remote_path, gzip, gunzip)

        return self._ph.execute_command('scp -C '
                                        '{ssh_opts} '
                                        "{path} {host}:{remote_path}".format(
                                                                    ssh_opts=self._ssh_opts,
                                                                    host=self._hostname,
                                                                    path=path,
                                                                    remote_path=remote_path
                                        ))

    def is_dir(self, path):
        ret, _, _ = self.execute_command('test -d {path}'.format(
                                                        path=path
                                      ))
        return ret == 0

    def exists(self, path):
        ret, _, _ = self.execute_command('test -e {path}'.format(
                                          path=path
                                      ))
        return ret == 0

    def mkdir(self, path, mode=0o700, recursive=True):
        ret, _, _ = self.execute_command('if [ ! -d {path} ]; then '
                                         'mkdir -p {path}; '
                                         'fi; {chmod_command}'.format(
                                             path=path,
                                             chmod_command='find {path}/ -type d -print0 |'
                                                           'xargs -0 chmod {mode}; '.format(
                                                                 path=os.path.split(path)[0],
                                                                 mode=oct(mode)
                                                           )
                                             if recursive else 'chmod {mode} {path}'.format(
                                                                         path=path,
                                                                         mode=oct(mode)
                                                               )
                                         ))

        return ret == 0

    def rmtree(self, path):
        ret, _, _ = self.execute_command('if [ -d {path} ]; then '
                                         'rm -rf {path}; '
                                         'fi'.format(path=path))

        return ret == 0
# endregion


__all__ = ['PopenHelper', 'PopenError', 'SshHelper']
