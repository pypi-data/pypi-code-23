import fnmatch
import logging
import os
import re
import time

from python_agent.build_scanner.entities.v3.build_mapping_request import BuildMappingRequest
from python_agent.build_scanner.file_scanner import FileScanner
from python_agent.common import constants
from python_agent.common.constants import DEFAULT_WORKSPACEPATH
from python_agent.common.http.backend_proxy import BackendProxy
from python_agent.utils import retries, get_top_relative_path, get_repo_url, get_commit_history

log = logging.getLogger(__name__)


def create_build_request(files, config_data):
    meta = {
        "generated": int(time.time() * 1000),
        "customerId": config_data.customerId,
        "appName": config_data.appName,
        "build": config_data.buildName,
        "branch": config_data.branchName,
        "technology": "python",
        "repositoryUrl": get_repo_url(),
        "history": get_commit_history()
    }
    request = BuildMappingRequest(meta, config_data, files, [])
    return request


@retries(log)
def send_build(files, config_data):
    body = create_build_request(files, config_data)
    backend_proxy = BackendProxy(config_data)
    backend_proxy.submit_build_mapping(body)
    log.info("Sent Build To Server. Number Of Files: %s" % len(files))


def filter_by_pattern(patterns, source_dir, subdir, files):
    filtered_files = set()
    for pattern in patterns:
        for basename in files:
            full_path = os.path.join(subdir, basename)
            if fnmatch.fnmatch(full_path, pattern):
                filtered_files.add(full_path)
    return filtered_files


def canonical_files(subdir, files):
    return map(lambda filename: os.path.join(subdir, filename), files)



def get_all_files(sources, includes=None, excludes=None):
    """
    :param sources: A list of directories or package names.
    If specified, only source inside these directories or packages will be scanned.

    :param includes: A list of file name patterns. If specified, only files matching those patterns will be measured

    :param excludes: A list of file name patterns, specifying files not to scan.

    If both include and omit are specified,
    first the set of files is reduced to only those that match the include patterns,
    then any files that match the omit pattern are removed from the set.

    :return: A list of full path python only files to be scanned
    """
    all_files = []
    if not sources:
        log.warning("Scan Sources Is Null Or Empty. No Files To Scan")
    for source_dir in sources:
        if os.path.isfile(source_dir):
            all_files.append(source_dir)
        for subdir, dirs, files in os.walk(source_dir):
            included_files = set(canonical_files(subdir, files))
            excluded_files = set()
            if includes:
                included_files = filter_by_pattern(includes, source_dir, subdir, files)
            if excludes:
                excluded_files.update(filter_by_pattern(excludes, source_dir, subdir, files))

            included_files = list(included_files - excluded_files)
            all_files.extend(included_files)

    all_files = [filename for filename in all_files if re.match(constants.PYTHON_FILES_REG, os.path.split(filename)[1])]
    return all_files


def main(config_data=None, workspacepath=None, include=None, exclude=None):
    try:
        workspacepath = workspacepath or [DEFAULT_WORKSPACEPATH]
        include = include or []
        exclude = exclude or []
        log.debug("Filtering Files. workspacepath: %s. include: %s. exclude: %s" % (workspacepath, include, exclude))
        files = get_all_files(workspacepath, include, exclude)
        log.debug("Starting Build Scan. Number Of Files: %s" % len(files))
        file_scanner = FileScanner()
        scanned_files = []
        for full_path in files:
            scanned_file = file_scanner.calculate_file_signature(full_path, get_top_relative_path(full_path))
            if scanned_file:
                scanned_files.append(scanned_file)

        if len(scanned_files) != len(files):
            log.warning("Number Of Scanned Files is Different From Total Files. Scanned: %s. Total: %s"
                        % (len(scanned_files), len(files)))
        if not scanned_files:
            log.warning("Total Scanned Files is 0. Not Sending Build To Server")
            return
        log.info("Sending Build To Server. Number Of Files: %s" % len(scanned_files))
        send_build(scanned_files, config_data)
    except Exception as e:
        log.exception("Failed Running Build Scan. Error: %s" % str(e))


if __name__ == '__main__':
    main()
