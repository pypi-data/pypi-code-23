import sys
import threading

from python_agent import admin, utils
from python_agent.test_listener.managers.agent_manager import AgentManager

try:
    admin.init()
except SystemExit as e:
    if sys.version_info >= (3, 0):
        threading.current_thread = utils.trace(threading.current_thread, AgentManager().get_trace_function())
    else:
        threading.currentThread = utils.trace(threading.currentThread, AgentManager().get_trace_function())
