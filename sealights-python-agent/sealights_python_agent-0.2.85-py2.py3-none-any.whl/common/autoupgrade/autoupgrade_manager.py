import logging
import os
import sys

import pip
from pip import status_codes

from python_agent.common.http.backend_proxy import BackendProxy

try:
    from pip import commands_dict
except ImportError:
    from pip import commands as commands_dict

from python_agent.packages import semantic_version
from python_agent import __version__ as CURRENT_VERSION, __package_name__ as PACKAGE_NAME

log = logging.getLogger(__name__)


class AutoUpgrade(object):
    def __init__(self, config_data):
        self.backend_proxy = BackendProxy(config_data)

    def get_recommended_version(self):
        response = self.backend_proxy.get_recommended_version()
        if not response:
            return self.get_current_version()
        agent = response.json().get("agent", {})
        version = agent.get("version")
        url = agent.get("url")
        log.info("Recommended Agent Version: %s" % version)
        return url, semantic_version.Version(version)

    def get_current_version(self):
        try:
            current_version = semantic_version.Version(CURRENT_VERSION)
            return current_version
        except Exception as e:
            log.warning("Failed Getting Current Version. Pkg. %s" % PACKAGE_NAME)
        return semantic_version.Version("0.0.0")

    def upgrade(self):
        current_version = self.get_current_version()
        log.info("Current Agent Version: %s" % current_version)
        url, recommended_version = self.get_recommended_version()
        status = status_codes.NO_MATCHES_FOUND
        if recommended_version != current_version:
            if self.is_version_exists_in_pypi(recommended_version):
                status = self.install_and_restart(PACKAGE_NAME + "==" + str(recommended_version))
        elif url:
            status = self.install_and_restart(url)
        return status

    def restart(self):
        os.execl(sys.executable, *([sys.executable] + sys.argv))

    def install_and_restart(self, recommended_version):
        try:
            log.info("Installing Agent Version: %s" % recommended_version)
            cmd_name, cmd_args = pip.parseopts([
                "install",
                recommended_version,
                "--ignore-installed"
            ])
            command = commands_dict[cmd_name]()
            options, args = command.parse_args(cmd_args)
            status = command.run(options, args)
            if status == status_codes.SUCCESS:
                log.info("Upgraded Agent Successfully. Restarting Agent With Version: %s" % recommended_version)
                self.restart()
            return status
        except SystemExit as e:
            log.info("Failed Upgrading Or Restarting Agent. System Exit: %s" % str(e))
            return status_codes.ERROR
        except Exception as e:
            log.info("Failed Upgrading Or Restarting Agent. Error: %s" % str(e))
            return status_codes.ERROR

    def is_version_exists_in_pypi(self, recommended_version):
        return self.backend_proxy.check_version_exists_in_pypi(recommended_version)
