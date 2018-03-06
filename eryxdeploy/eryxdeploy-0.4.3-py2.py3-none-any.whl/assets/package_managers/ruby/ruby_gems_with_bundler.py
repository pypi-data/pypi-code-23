from eryx_deploy.assets.package_managers.abs_package_manager import PackageManager


class RubyGemsWithBundler(PackageManager):
    def __init__(self, ruby_environment):
        self._ruby_environment = ruby_environment

    def first_time_setup(self):
        self._ruby_environment.run("gem install bundler")
        self._do_not_generate_docs_for_gems()

    def update_dependencies(self):
        self._ruby_environment.run("bundle install")

    def _do_not_generate_docs_for_gems(self):
        self._ruby_environment.run('echo "gem: --no-document" > ~/.gemrc')
