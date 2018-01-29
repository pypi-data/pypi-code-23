# coding: utf8

import sys
import time
import getpass
from crontab import CronTab

from .core.errors import ApiError
from .utils import convert_path_to_name


def get_cron():
    return CronTab(user=getpass.getuser())


class Job(object):

    def __init__(self):
        self.id = None
        self.name = None
        self.trigger = None
        self.next_run_at = None

    def to_api_json(self):
        return dict(
            id=self.id,
            name=self.name,
            trigger=str(self.trigger),
            next_run_at=str(self.next_run_at)
        )

    @classmethod
    def get(cls, id, type):
        for job in cls.get_list(type):
            if job.id == id:
                return job

    @classmethod
    def get_by_name(cls, name, type):
        return cls.get_dict(type).get(name)

    @classmethod
    def add(cls, name, trigger, type):
        from .template import Template
        from .script import Script

        if not trigger or trigger == '* * * * *':
            raise ApiError('trigger 非法')

        job_id = str(int(time.time()))
        cron = get_cron()

        if type == 'template':
            template = Template.get_dict().get(name)
            if not template:
                raise ApiError('template:{} not found'.format(name))
            each = cron.new(command='{} {} -m d'.format(sys.executable, template.path))
        else:
            script = Script.get_dict().get(name)
            if not script:
                raise ApiError('script:{} not found'.format(name))
            each = cron.new(command='{} {}'.format(sys.executable, script.path))

        each.setall(trigger)
        each.set_comment(job_id)
        if each.is_valid():
            each.enable()
            cron.write()
            return True
        else:
            return False

    def delete(self):
        cron = get_cron()
        for job in cron.find_comment(self.id):
            cron.remove(job)
            cron.write()

    @classmethod
    def get_list(cls, type):
        from . import env

        jobs = []
        for each in get_cron():
            splits = each.command.split()
            if len(splits) < 2:
                continue
            python, path = splits[:2]
            if python != sys.executable:
                continue
            if (type == 'template' and env.TEMPLATES_DIR in path) or (type == 'script' and env.SCRIPTS_DIR in path):
                job = Job()
                job.id = each.comment
                job.name = convert_path_to_name(path, type)
                job.trigger = each.slices
                job.next_run_at = each.schedule().get_next()
                jobs.append(job)

        return jobs

    @classmethod
    def get_dict(cls, type):
        return {
            job.name: job
            for job in cls.get_list(type)
        }
