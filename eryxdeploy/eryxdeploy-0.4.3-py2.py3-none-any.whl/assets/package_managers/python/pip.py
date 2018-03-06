from eryx_deploy.assets.package_managers.python.abs_python import PythonPackageManager


class Pip(PythonPackageManager):
    def first_time_setup(self):
        self._python_environment.first_time_setup()

    def update_dependencies(self):
        if self._python_environment.python_major_version() == 3:
            self._python_environment.run('pip3 install -Ur %s' % self._requirements_file_path)
        else:
            self._python_environment.run('pip install -Ur %s' % self._requirements_file_path)
