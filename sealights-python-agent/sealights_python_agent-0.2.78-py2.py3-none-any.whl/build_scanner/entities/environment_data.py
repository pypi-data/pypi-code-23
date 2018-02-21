import os
import platform
import socket
import uuid

import pkg_resources

from python_agent import __version__ as VERSION


class EnvironmentData(object):
    agentId = None

    def __init__(self, lab_id, test_stage):
        self.labId = lab_id
        self.testStage = test_stage
        if not EnvironmentData.agentId:
            EnvironmentData.agentId = str(uuid.uuid4())
        self.agentId = EnvironmentData.agentId
        self.agentType = "python"
        self.agentVersion = VERSION
        self.machineName = socket.gethostname()
        self.platform = platform.platform()
        self.os = platform.system()
        self.osVersion = platform.release()
        self.arch = platform.machine()
        self.processId = os.getpid()
        self.dependencies = dict((package_name, pkg_resources.require(package_name)[0].version)
                                 for package_name, class_name in pkg_resources.working_set.by_key.items())
        self.compiler = platform.python_compiler()
        self.interpreter = platform.python_implementation()
        self.runtime = platform.python_version()
