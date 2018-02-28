import logging
import os
import re

from python_agent.common import constants
from python_agent.test_listener.footprints_collector import FootprintsCollector
from python_agent.utils import get_top_relative_path

log = logging.getLogger(__name__)


class LineFootprintsCollector(FootprintsCollector):

    def get_footprints_and_clear(self, coverage_object):
        footprints = []
        for filename, covered_lines in coverage_object._lines.items():
            if not re.match(constants.PYTHON_FILES_REG, os.path.split(filename)[1]):
                continue

            file_footprints = map(
                lambda line: {
                    "unique_id": get_top_relative_path(filename) + "|" + str(line),
                    "hits": 1,
                    "filename": filename
                },
                covered_lines.keys()
            )
            if file_footprints:
                footprints.extend(file_footprints)
        return footprints
