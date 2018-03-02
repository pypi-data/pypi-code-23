from __future__ import print_function

import os
import hashlib
from time import sleep
# import random
import pkg_resources
import requests
import sys
import json
from pathlib2 import PurePath
from shutil import (
    copyfile,
    rmtree,
    copytree,
    ignore_patterns
)

from russell.manager.data_config import DataConfigManager

from russell.manager.experiment_config import ExperimentConfigManager

from russell.manager.auth_config import AuthConfigManager

from russell.exceptions import RussellException

import russell
import time
from russell.constants import LOADING_MESSAGES
from russell.log import logger as russell_logger
from russell.manager.russell_ignore import RussellIgnoreManager


def get_task_url(id, gpu=False, view="notebook"):
    """
    Return the url to proxy to a running task
    """
    if gpu:
        return "{}/{}/{}/".format(russell.russell_gpu_host, view, id)
    else:
        return "{}/{}/{}/".format(russell.russell_cpu_host, view, id)


def get_module_task_instance_id(task_instances):
    """
    Return the first task instance that is a module node.
    """
    for id in task_instances:
        if task_instances[id] == 'module_node':
            return id
    return None


def get_mode_parameter(mode):
    """
    Map the mode parameter to the server parameter
    """
    if mode == 'job':
        return 'cli'
    elif mode == 'serve':
        return 'serving'
    else:
        return mode


def wait_for_url(url, status_code=200, sleep_duration_seconds=1, iterations=120, message_frequency=15):
    """
    Wait for the url to become available
    """
    for iteration in range(iterations):
        # if(iteration % message_frequency == 0):
        #     print("\n{}".format(random.choice(LOADING_MESSAGES)), end='', flush=True)

        # print(".", end='', flush=True)
        # print (url)
        try:
            response = requests.get(url)
        except:
            return False
        if response.status_code == status_code:
            # print(".", flush=True)
            return True
        sleep(sleep_duration_seconds)
    # print(".", flush=True)
    return False


def getPythonVersion():
    if sys.version_info < (3, 0):
        return 2
    else:
        return 3


def force_unicode(s, encoding='UTF-8'):
    if getPythonVersion() == 2:
        try:
            return unicode(s)
        except UnicodeDecodeError:
            return str(s).decode(encoding, 'replace')
    else:
        if isinstance(s, bytes):
            s = bytes.decode(s)
        return str(s)


def py2code():
    if getPythonVersion() == 2:
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')


def get_size(path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def get_md5_checksum(filename):
    if not os.path.isfile(filename):
        raise Exception("No such file found: {}".format(filename))
    with open(filename, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(2 ** 20)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def sizeof_fmt(num, suffix='B'):
    """
    Print in human friendly format
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def copy_files(src, target):
    if os.path.exists(target):
        rmtree(target)
    ignore_list, whitelist = RussellIgnoreManager.get_list()
    ignore_list_expanded = ignore_list + ["{}/**".format(item) for item in ignore_list]
    copytree(src, target, ignore=ignore_patterns(*ignore_list_expanded))


def matches_glob_list(path, glob_list):
    """
    Given a list of glob patterns, returns a boolean
    indicating if a path matches any glob in the list
    """
    for glob in glob_list:
        try:
            if PurePath(path).match(glob):
                return True
        except TypeError:
            pass
    return False


def unix_style_path(path):
    if os.path.sep != '/':
        return path.replace(os.path.sep, '/')
    return path


def ignore_path(path, ignore_list=None, whitelist=None):
    """
    Returns a boolean indicating if a path should be ignored given an
    ignore_list and a whitelist of glob patterns.
    """
    if ignore_list is None:
        ignore_list = []
    if whitelist is None:
        whitelist = []
    return matches_glob_list(path, ignore_list) and not matches_glob_list(path, whitelist)


def get_unignored_file_paths(ignore_list=None, whitelist=None):
    """
    Given an ignore_list and a whitelist of glob patterns, returns the list of
    unignored file paths in the current directory and its subdirectories
    """
    unignored_files = []
    if ignore_list is None:
        ignore_list = []
    if whitelist is None:
        whitelist = []

    for root, dirs, files in os.walk("."):
        russell_logger.debug("Root:%s, Dirs:%s", root, dirs)

        if ignore_path(unix_style_path(root), ignore_list, whitelist):
            dirs[:] = []
            russell_logger.debug("Ignoring directory : %s", root)
            continue

        for file_name in files:
            file_path = unix_style_path(os.path.join(root, file_name))
            if ignore_path(file_path, ignore_list, whitelist):
                russell_logger.debug("Ignoring file : %s", file_name)
                continue

            unignored_files.append(os.path.join(root, file_name))

    return unignored_files


def get_files_in_current_directory(file_type):
    file_count = 0
    total_file_size = 0

    ignore_list, whitelist = RussellIgnoreManager.get_list()

    russell_logger.debug("Ignoring: %s", ignore_list)
    russell_logger.debug("Whitelisting: %s", whitelist)

    file_paths = get_unignored_file_paths(ignore_list, whitelist)

    for file_path in file_paths:
        file_count += 1
        total_file_size += os.path.getsize(file_path)

    return file_count, total_file_size


def get_files_in_directory(path, file_type):
    """
    Gets the list of files in the directory and subdirectories
    Respects .russellignore file if present
    """
    local_files = []
    separator = os.path.sep
    ignore_list, whitelist = RussellIgnoreManager.get_list()

    # make sure that subdirectories are also excluded
    ignore_list_expanded = ignore_list + ["{}/**".format(item) for item in ignore_list]
    russell_logger.debug("Ignoring list : {}".format(ignore_list))
    total_file_size = 0

    for root, dirs, files in os.walk(path):
        russell_logger.debug("Root:{}, Dirs:{}".format(root, dirs))
        ignore_dir = False
        normalized_path = normalize_path(path, root)
        for item in ignore_list_expanded:
            if PurePath(normalized_path).match(item):
                ignore_dir = True
                break

        if ignore_dir:
            # Reset dirs to avoid going further down this directory
            dirs[:] = []
            russell_logger.debug("Ignoring directory : {}".format(root))
            continue

        for file_name in files:
            ignore_file = False
            normalized_path = normalize_path(path, os.path.join(root, file_name))
            for item in ignore_list_expanded:
                if PurePath(normalized_path).match(item):
                    ignore_file = True
                    break

            if ignore_file:
                russell_logger.debug("Ignoring file : {}".format(normalized_path))
                continue

            file_relative_path = os.path.join(root, file_name)
            if separator != '/':  # convert relative paths to Unix style
                file_relative_path = file_relative_path.replace(os.path.sep, '/')
            file_full_path = os.path.join(os.getcwd(), root, file_name)

            local_files.append((file_type, (file_relative_path, open(file_full_path, 'rb'), 'text/plain')))
            total_file_size += os.path.getsize(file_full_path)

    return (local_files, sizeof_fmt(total_file_size), total_file_size)


def save_dir(file_list, target):
    if os.path.exists(target):
        rmtree(target)
    os.mkdir(target)
    for file in file_list:
        src_path = file[-1][0]
        path = os.path.dirname(src_path)
        path = os.path.join(path, target)
        if not os.path.exists(path):
            os.makedirs(path)
        dst_path = os.path.join(target, src_path.split('/')[-1])
        copyfile(src_path, dst_path)
    return True


def get_file_list_in_dir(path):
    """
    Gets the list of files in the directory and subdirectories
    Respects .russellignore file if present
    """
    local_files = []
    separator = os.path.sep
    ignore_list, whitelist = RussellIgnoreManager.get_list()

    # make sure that subdirectories are also excluded
    ignore_list_expanded = ignore_list + ["{}/**".format(item) for item in ignore_list]
    russell_logger.debug("Ignoring list : {}".format(ignore_list))

    for root, dirs, files in os.walk(path):
        russell_logger.debug("Root:{}, Dirs:{}".format(root, dirs))
        ignore_dir = False
        normalized_path = normalize_path(path, root)
        for item in ignore_list_expanded:
            if PurePath(normalized_path).match(item):
                ignore_dir = True
                break

        if ignore_dir:
            # Reset dirs to avoid going further down this directory
            dirs[:] = []
            russell_logger.debug("Ignoring directory : {}".format(root))
            continue

        for file_name in files:
            ignore_file = False
            normalized_path = normalize_path(path, os.path.join(root, file_name))
            for item in ignore_list_expanded:
                if PurePath(normalized_path).match(item):
                    ignore_file = True
                    break

            if ignore_file:
                russell_logger.debug("Ignoring file : {}".format(normalized_path))
                continue

            file_relative_path = os.path.join(root, file_name)
            if separator != '/':  # convert relative paths to Unix style
                file_relative_path = file_relative_path.replace(os.path.sep, '/')
            # file_full_path = os.path.join(os.getcwd(), root, file_name)

            local_files.append(file_relative_path)

    return local_files


# def transfer2bin(file_list, target):
#     if os.path.exists(target):
#         rmtree(target)
#     os.mkdir(target)

def get_file_count(path):
    def counter(path, file_count=0):
        for lists in os.listdir(path):
            sub_path = os.path.join(path, lists)
            if os.path.isfile(sub_path):
                file_count += 1
            elif os.path.isdir(sub_path):
                file_count += counter(sub_path)
        return file_count

    return counter(path)


def normalize_path(project_root, path):
    """
    Convert `path` to a UNIX style path, where `project_root` becomes the root
    of an imaginery file system (i.e. becomes just an initial "/").
    """
    if os.path.sep != '/':
        path = path.replace(os.path.sep, '/')
        project_root = project_root.replace(os.path.sep, '/')

    path = path[len(project_root):] if path.startswith(project_root) else path
    path = '/' + path if not path.startswith('/') else path

    return path


def get_cli_version():
    return pkg_resources.require("floyd-cli")[0].version


def current_username():
    return AuthConfigManager.get_access_token().username


def current_experiment_name():
    return ExperimentConfigManager.get_config().name


def current_dataset_name():
    return DataConfigManager.get_config().name


class ProgressBar(object):
    """
    上传或下载用的进度显示条
    """

    def __init__(self, title,
                 count=0.0,
                 run_status=None,
                 fin_status=None,
                 total=100.0,
                 unit='', sep='/',
                 chunk_size=1.0):
        """
        :param title: 进度条标题，一般为文件名
        :param count: 当前已下载的文件大小，若刚开始则为0
        :param run_status: 下载状态的提示语
        :param fin_status: 下载结束状态的提示语
        :param total: 下载文件的总大小
        :param unit: 单位
        :param sep: 进度和总数间的分割线
        :param chunk_size: 下载块大小
        """
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s %s/s             "
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep
        self.last_count = 0
        self.last_time = time.time()
        self.speed = 0
        self.refresh_max_cnt = 100
        self.refresh_cnt = 0

    def __get_info(self):
        """
        :return: [名称] 状态 进度 单位 分割线 总数 单位 下载速度

        """
        _info = self.info % (self.title, self.status,
                             self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size, self.unit,
                             sizeof_fmt(self.speed))
        return _info

    def refresh(self, count=1, status=None):
        """
        :param count: 文件下载的字节数
        :param status: 自定义状态文字
        :return:
        """
        self.count += count
        if self.refresh_cnt < self.refresh_max_cnt:
            self.refresh_cnt += 1
            return
        end_time = float(time.time())
        self.refresh_cnt = 0
        division = float(end_time - self.last_time)
        if division:
            self.speed = (self.count - self.last_count) / division
            self.last_time = end_time
            self.last_count = self.count
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status

        print(self.__get_info(), end=end_str)
