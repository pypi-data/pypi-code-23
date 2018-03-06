from eryx_deploy.assets.package_managers.frontend.abs_frontend import FrontendPackageManager


class Yarn(FrontendPackageManager):
    def first_time_setup(self):
        self._host_machine.install_nodejs()
        self._host_machine.install_yarn()

    def update_dependencies(self):
        with self._host_machine.cd_project():
            self._host_machine.run("yarn install")
