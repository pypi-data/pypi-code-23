from python_agent.common import constants


class ConfigData(object):
    def __init__(self, token, customer_id, server, proxy, build_session_id, is_compress=True):
        self.token = token
        self.server = server
        self.proxy = proxy
        self.isCompress = is_compress
        self.buildSessionId = build_session_id
        self.customerId = customer_id
        self.appName = None
        self.buildName = None
        self.branchName = None
        self.labId = None
        self.testStage = constants.DEFAULT_ENV
        self.additionalParams = {}
        self.workspacepath = None
        self.include = None
        self.exclude = None
        self.isInitialColor = True
        self.initialColor = constants.INITIAL_COLOR
        self.args = None
        self.program = None
        self.isSendLogs = False
        self.isOfflineMode = False
