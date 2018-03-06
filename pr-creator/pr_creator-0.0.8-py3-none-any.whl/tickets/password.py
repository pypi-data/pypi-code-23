import subprocess


class Password(object):

    def __str__(self):
        """ Get the user password from the keychain or fail."""

        command = '/usr/bin/security find-generic-password -wl abcemployees'.split(' ')
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        password = process.stdout.read().strip()
        if password is None:
            raise RuntimeError(
                'We need your abcemployees password on your keychain, or specify one via JIRA_PASSWD as an env var.'
            )

        return password
