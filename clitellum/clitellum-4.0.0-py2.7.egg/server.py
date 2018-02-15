from clitellum.processors import builders
from clitellum.core.fsm import Startable
from clitellum.handlers import HandlerManager
from clitellum.core.bus import Identification

__author__ = 'sergio'


## Crea un server desde un config
def create_server_from_config(cfg):
    identification = Identification(cfg['identification']['id'], cfg['identification']['type'])
    ag = builders.create_agent_from_config(identification, cfg["agent"])
    control = builders.create_agent_from_config(identification, cfg["controller"])
    return Server(identification, ag, control)

class Server(Startable):

    def __init__(self, identification, agent, controller):
        Startable.__init__(self)
        self.identification = identification
        self.handler_manager = HandlerManager()
        self._agent = agent
        self._agent.configure(self.handler_manager)
        self._controller = controller

    def _invokeOnStart(self):
        Startable._invokeOnStart(self)
        self._agent.start()
        self._controller.start()

    def _invokeOnStopped(self):
        Startable._invokeOnStopped(self)
        self._agent.stop()
        self._controller.stop()

    def __del__(self):
        Startable.__del__(self)


