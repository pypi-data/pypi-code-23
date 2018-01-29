import os.path

from tcell_agent.tcell_logger import get_module_logger

from .appsensor_rule_manager import AppSensorRuleManager


rule_manager = AppSensorRuleManager()
try:
    basepath = os.path.dirname(__file__)
    baserulesfilename = os.path.abspath(os.path.join(basepath, "python-baserules.json"))
    rule_manager.load_rules_file(baserulesfilename)
except Exception as read_rules_exception:
    LOGGER = get_module_logger(__name__)
    LOGGER.error("Problem reading baserules: {e}".format(e=read_rules_exception))
    LOGGER.debug(read_rules_exception, exc_info=True)
