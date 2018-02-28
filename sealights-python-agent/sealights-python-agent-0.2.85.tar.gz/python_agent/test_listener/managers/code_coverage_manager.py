import logging
import threading

import os

import python_agent
from python_agent.common import constants
from python_agent.test_listener.line_footprints_collector import LineFootprintsCollector
from python_agent.test_listener.method_footprints_collector import MethodFootprintsCollector

try:
    from coverage import Coverage, CoverageData
except ImportError:
    from coverage import coverage as Coverage

log = logging.getLogger(__name__)


class CodeCoverageManager(object):
    def __init__(self, config_data):
        self.coverage = Coverage(source=config_data.workspacepath, include=config_data.include, omit=config_data.exclude)
        if getattr(self.coverage, "_warn_no_data", False):
            self.coverage._warn_no_data = False
        if config_data.isOfflineMode:
            # no actual tracing is done here
            # we're loading the raw coverage data from the .coverage file
            # so coverage.get_data() will return it and we'll convert it to footprints
            self.coverage.load()
        else:
            self.coverage.start()
        self.coverage_lock = threading.Lock()
        self.coverage_collectors = {}
        self.coverage_collectors["methods"] = MethodFootprintsCollector()
        # self.coverage_collectors["lines"] = LineFootprintsCollector()
        log.info("Started Code Coverage Manager")

    def get_footprints_and_clear(self):
        footprints = {}
        with self.coverage_lock:
            # get_data creates or updates coverage.data with the CoverageData object and
            # clears counters on the collector but not on the coverage.data object
            # we make sure to clear coverage.data as well by creating a new one
            coverage_object = self.coverage.get_data()
            self.reset_coverage(coverage_object)
            if not coverage_object:
                log.info("No Coverage Found")
                return footprints

            for coverage_type, coverage_collector in self.coverage_collectors.items():
                footprints[coverage_type] = coverage_collector.get_footprints_and_clear(coverage_object)
        return footprints

    def shutdown(self):
        self.coverage.stop()
        if constants.IN_TEST:
            # combine raw coverage with the coverage we have so far
            # normalize agent paths and save for debugging
            self.coverage.combine()
            # self.normalize_agent_paths()
            self.coverage.data_suffix = str(os.getpid())
            self.coverage.save()
        log.info("Finished Shutting Down Code Coverage Manager")

    def register_collector(self, coverage_type, collector):
        self.coverage_collectors[coverage_type] = collector

    def get_trace_function(self):
        return self.coverage.collector._installation_trace

    def reset_coverage(self, coverage_object):
        self.coverage.data = CoverageData(debug=self.coverage.debug)
        if constants.IN_TEST:
            # for self test we add back agent related coverage
            self.coverage.data._lines = {}
            for filename, covered_lines in coverage_object._lines.items():
                if python_agent.__name__ in filename:
                    self.coverage.data._lines[filename] = covered_lines

    def normalize_agent_paths(self):
        for filename in self.coverage.data._lines.keys():
            if "/" + python_agent.__name__ in filename:
                python_agent_path = os.path.dirname(os.path.dirname(python_agent.__file__)).replace("/local/lib/", "/lib/") + "/"
                normalized_filename = filename.replace(python_agent_path, "")
                self.coverage.data._lines[normalized_filename] = self.coverage.data._lines.pop(filename)
