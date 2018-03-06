from eryx_deploy.assets.abs_executable_environment import ExecutableEnvironment
from eryx_deploy.utils.interactive_console import InteractiveConsole


class Rbenv(ExecutableEnvironment):

    def __init__(self, host_machine, ruby_version='2.3.4'):
        self._host_machine = host_machine
        self._ruby_version = ruby_version
        self._env_vars = {}

    def set_env_var(self, key, value):
        self._env_vars[key] = value

    def get_env_var(self, key):
        return self._env_vars[key]

    def first_time_setup(self):
        self._host_machine.install_rbenv()
        self._install_ruby()

    # def refresh_env(self):
    #     self._host_machine.run('rbenv rehash')

    def ruby_version_env_var_key(self):
        """
        Key used to set the ruby version with this environment
        @return:
        """
        return 'RBENV_VERSION'

    def ruby_version(self):
        return self._ruby_version

    # decorated methods

    def _call_on_host(self, method, *args, **kwargs):
        """
        Call a method on the host machine, setting the environment before
        @param method:
        @param args:
        @param kwargs:
        @return:
        """
        with self._host_machine.cd_project():
            with self._set_ruby_version():
                with self._host_machine.env_vars(self._env_vars):
                    return getattr(self._host_machine, method)(*args, **kwargs)

    def run(self, command, on_fail_msg=None):
        return self._call_on_host('run', command, on_fail_msg)

    def command_path(self, command):
        return self._call_on_host('command_path', command)

    # private

    def _install_ruby(self):
        if self._check_if_needed_version_is_installed():
            InteractiveConsole.show_info("Ruby %s already installed. Skipping." % self.ruby_version())
            return

        self._host_machine.install_ruby_compile_depedencies()
        self._host_machine.run('rbenv install -v %s' % self._ruby_version)

    def _set_ruby_version(self):
        return self._host_machine.prefix('rbenv shell %s' % self._ruby_version)

    def _check_if_needed_version_is_installed(self):
        not_installed_msg = "rbenv: version `%s' not installed" % self._ruby_version
        check_msg = "Checking if ruby %s is already installed..." % self.ruby_version()
        return self._host_machine.run_check('rbenv shell %s' % self._ruby_version,
                                            message=check_msg) != not_installed_msg
