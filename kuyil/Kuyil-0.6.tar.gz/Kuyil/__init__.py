from os import path, remove
import logging
import logging.config
import json
import os
import sys

sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../'))

# If applicable, delete the existing log file to generate a fresh log file during each execution
if path.isfile("python_logging.log"):
    remove("python_logging.log")

"""
with open("config.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)

logging.config.dictConfig(config_dict)
"""
# Log that the logger was configured
logger = logging.getLogger(__name__)
logger.info('Completed configuring logger()!')