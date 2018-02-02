# coding: utf8

import os
import sys
import subprocess
import psutil
from .core.errors import ApiError
from .utils import utc2datetime, time_readable, convert_path_to_name
from . import env


class Process(object):

    def __init__(self):
        self.id = None
        self.name = None
        self.path = None
        self.memory_percent = None
        self.thread_num = None
        self.create_at = None
        self._process = None

    @property
    def cpu_percent(self):
        return self._process.cpu_percent(interval=0.1)

    def kill(self):
        self._process.kill()

    def to_api_json(self):
        return dict(
            id=self.id,
            name=self.name,
            cpu_percent=self.cpu_percent,
            memory_percent=self.memory_percent(),
            create_at=self.create_at and time_readable(self.create_at) or None,
        )

    @classmethod
    def add(cls, name, type):
        from fastgets.template import Template
        from fastgets.script import Script

        if name in cls.get_dict(type):
            raise ApiError('不能重复启动')

        if type == 'template':
            template = Template.get_dict().get(name)
            if not template:
                raise ApiError('模板不存在')

            cmdline = [sys.executable, template.path, '-m', 'd']

        elif type == 'script':
            script = Script.get_dict().get(name)
            if not script:
                raise ApiError('脚本不存在')

            cmdline = [sys.executable, script.path]

        else:
            raise ApiError('type is error')

        dev_null = open(os.devnull, 'wb')

        subprocess.Popen(
            cmdline,
            stdout=dev_null, stderr=dev_null, stdin=dev_null, close_fds=True
        )

    @classmethod
    def get_type(cls, _process):
        try:
            cmdline = _process.cmdline()
            if len(cmdline) >= 2:
                if env.TEMPLATES_DIR in cmdline[1]:
                    return 'template'
                if env.SCRIPTS_DIR in cmdline[1]:
                    return 'script'
        except psutil.AccessDenied:
            pass
        except psutil.ZombieProcess:
            pass

    @classmethod
    def _get(cls, _process):
        process = Process()
        process.id = str(_process.pid)
        process.path = _process.cmdline()[1]
        if env.TEMPLATES_DIR in process.path:
            process.name = convert_path_to_name(process.path, 'template')
        else:
            process.name = convert_path_to_name(process.path, 'script')

        process.memory_percent = _process.memory_percent
        process.thread_num = _process.num_threads()
        process.create_at = utc2datetime(_process.create_time())
        process._process = _process
        return process

    @classmethod
    def get(cls, id):
        _process = psutil.Process(int(id))
        return cls._get(_process)

    @classmethod
    def get_list(cls, type):
        process_list = []
        for pid in psutil.pids():
            _process = psutil.Process(pid)
            if cls.get_type(_process) == type:
                process_list.append(cls._get(_process))

        return process_list

    @classmethod
    def get_dict(cls, type):
        return {
            process.name: process
            for process in cls.get_list(type)
        }
