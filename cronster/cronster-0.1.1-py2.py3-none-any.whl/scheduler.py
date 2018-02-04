#!/usr/bin/env python
import cmd
import sys
import json
import time
import subprocess
from datetime import datetime
from threading import Thread

import click
import redis
from croniter import croniter
from tabulate import tabulate

CRONSTER = """
                              __
  ______________  ____  _____/ /____  _____
 / ___/ ___/ __ \/ __ \/ ___/ __/ _ \/ ___/
/ /__/ /  / /_/ / / / (__  ) /_/  __/ /
\___/_/   \____/_/ /_/____/\__/\___/_/

"""


class CronsterScheduler(object):
    """
    Cronster scheduler class. Load jobs from a Redis cache and run any number
    of :class:`~cronster.scheduler.CronsterJob` based on their schedule.
    """
    def __init__(self, cache_host, cache_port):
        """
        Initialise a :class:`~cronster.scheduler.CronsterScheduler`.

        :param cache_host: Host that serves the Redis cache
        :type cache_host: str
        :param cache_port: Port on the host that exposes the Redis service
        :type cache_port: int
        """
        self.cache = redis.StrictRedis(
            host=cache_host, port=cache_port, db=0)
        self.jobs = []
        self.running = True

    def run_pending(self):
        """Run all pending jobs."""
        if not self.running:
            return
        for job in sorted([job for job in self.jobs if job.is_due]):
            job.run()

    def clear(self):
        """Clear the job queue."""
        self.jobs = []

    def update(self):
        """
        Load the current cache contents, add jobs or change jobs' statuses.
        """
        cached_jobs = json.loads(self.cache.get('cronster_crawler'))

        cached_hashes = [job['hash'] for job in cached_jobs]
        existing_hashes = [job.hash for job in self.jobs]

        # Check existing jobs and update their statuses where appropriate
        for job in self.jobs:
            if job.hash in cached_hashes:
                if not job.status:
                    job.status = True
            else:
                job.status = False
        # Check cached jobs and add them to the scheduler if they don't exist
        for job in cached_jobs:
            if job['hash'] in existing_hashes:
                continue
            self.jobs.append(
                CronsterJob(
                    job['name'],
                    job['cmd'],
                    job['schedule'],
                    job['path'],
                    job['hash']))

    def start(self):
        """
        Start the scheduler. Jobs will be run according to their schedule.
        """
        self.running = True

    def stop(self):
        """
        Stop the scheduler. Jobs will not be running regardless of their
        schedule.
        """
        self.running = False

    def status(self):
        """
        Return the current status of all scheduler jobs.

        :return: Job data
        :rtype: tuple
        """
        metadata = [
            [
                'Cronster Scheduler'
            ],
            [
                'Status: ',
                'Running' if self.running else 'Stopped'
            ],
            [
                'Update time: ',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ],
            [
                'Number of jobs: ',
                len(self.jobs)
            ],
            [
                'Number of active jobs: ',
                len([job for job in self.jobs if job.status])
            ]
        ]
        headers = ['Job Name', 'Schedule', 'Last run', 'Next run']
        job_data = []
        for job in sorted(self.jobs):
            job_data.append([
                job.name,
                job.cron,
                job.last_run if job.last_run else 'N/A',
                job.next_run if job.status else 'N/A'])
        return metadata, headers, job_data

    def __repr__(self):
        return '<CronsterScheduler>'

    def __str__(self):
        return str({
            'cache': self.cache,
            'jobs': self.jobs,
            'running': self.running
        })


class CronsterJob(object):
    """
    Cronster job class. Representation of an individual cronster job.
    """
    def __init__(self, job_name, job_cmd, job_schedule, job_path, job_hash):
        """
        Initialise a :class:`~cronster.scheduler.CronsterJob`.

        :param job_name: Job name
        :type job_name: str
        :param job_cmd: Job command
        :type job_cmd: str
        :param job_schedule: Job schedule in cron format, e.g. ``*/5 * * * *``
        :type job_schedule: str
        :param job_path: Job's crontab file path
        :type job_path: str
        :param job_hash: Job hash
        :type job_hash: str
        """
        self._name = job_name
        self._cmd = job_cmd
        self._cron = job_schedule
        self._path = job_path
        self._hash = job_hash
        self._status = True
        self.last_run = None
        self.next_run = None
        self.schedule()

    @property
    def name(self):
        """
        :return: Job name
        :rtype: str
        """
        return self._name

    @property
    def cmd(self):
        """
        :return: Job command
        :rtype: str
        """
        return self._cmd

    @property
    def cron(self):
        """
        :return: Job schedule
        :rtype: str
        """
        return self._cron

    @property
    def path(self):
        """
        :return: Job crontab file path
        :rtype: str
        """
        return self._path

    @property
    def hash(self):
        """
        :return: Job hash
        :rtype: str
        """
        return self._hash

    @property
    def status(self):
        """
        :return: Job status
        :rtype: bool
        """
        return self._status

    @status.setter
    def status(self, value):
        """
        Given a new ``value``, set job status.
        Schedule the job if the job is now active.

        :param value: New status value
        :type value: bool
        """
        self._status = value
        if value:
            self.schedule()

    @property
    def is_due(self):
        """
        :return: Whether or not the job is due to be run.
        :rtype: bool
        """
        return datetime.now() >= self.next_run

    def schedule(self):
        """Calculate the next run time and schedule the job to run."""
        base = datetime.now()
        cron_iter = croniter(self.cron, base)
        self.next_run = cron_iter.get_next(datetime)

    def _execute_command(self):
        """Execute the job's command as a subprocess."""
        subprocess.check_call(self.cmd, shell=True)

    def run(self):
        """Run the job and schedule the next run."""
        if not self.status:
            return
        self._execute_command()
        self.last_run = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.schedule()

    def __lt__(self, other):
        return self.next_run < other.next_run

    def __repr__(self):
        return '<CronsterJob>'

    def __str__(self):
        return str({
            'name': self._name,
            'cmd': self._cmd,
            'schedule': self._cron,
            'path': self._path,
            'hash': self._hash,
            'status': self._status,
            'last_run': self.last_run,
            'next_run': self.next_run
        })


class CronsterSchedulerPrompt(cmd.Cmd):
    """
    Cronster command prompt class. Implement CLI commands to control the
    attached :class:`~cronster.scheduler.CronsterScheduler`.
    """
    def __init__(self, scheduler):
        """
        Initialise a :class:`~cronster.scheduler.CronsterSchedulerPrompt`.

        :param scheduler: Scheduler to control
        :type scheduler: :class:`~cronster.scheduler.CronsterScheduler`
        """
        super(CronsterSchedulerPrompt, self).__init__()
        self.scheduler = scheduler
        click.clear()
        self.prompt = '> '

    def do_status(self, args):
        """
        Invoke :func:`cronster.scheduler.CronsterScheduler.status()` and print
        the status information to the console.
        """
        metadata, headers, job_data = self.scheduler.status()
        click.clear()
        print(tabulate(metadata))
        print('\n')
        print(tabulate(job_data, headers=headers))
        print('\n')

    def do_update(self, args):
        """
        Invoke :func:`cronster.scheduler.CronsterScheduler.update()` to force
        a job update form the cache.
        """
        self.scheduler.update()

    def do_clear(self, args):
        """
        Invoke :func:`cronster.scheduler.CronsterScheduler.clear()` to clear
        the job queue.
        """
        self.scheduler.clear()

    def do_start(self, args):
        """
        Invoke :func:`cronster.scheduler.CronsterScheduler.start()` to start
        the scheduler.
        """
        self.scheduler.start()

    def do_stop(self, args):
        """
        Invoke :func:`cronster.scheduler.CronsterScheduler.stop()` to stop
        the scheduler.
        """
        self.scheduler.stop()

    def do_exit(self, args):
        """
        Close the scheduler.
        """
        sys.exit(0)

    def __repr__(self):
        return '<CronsterSchedulerPrompt>'

    def __str__(self):
        return str({
            'scheduler': self.scheduler
        })


def _update_loop(scheduler):
    """
    Run an infinite update/run loop.

    :param scheduler: Scheduler to run
    :type scheduler: :class:`~cronster.scheduler.CronsterScheduler`
    """
    while True:
        scheduler.update()
        scheduler.run_pending()
        time.sleep(1)


def run_scheduler(cache_host, cache_port):
    """
    Instantiate and run a :class:`~cronster.scheduler.CronsterScheduler`.
    Run its run/update loop in a separate thread.

    :param cache_host: Host that serves the Redis cache
    :type cache_host: str
    :param cache_port: Port on the host that exposes the Redis service
    :type cache_port: int
    """
    scheduler = CronsterScheduler(cache_host, cache_port)
    update_loop_thread = Thread(target=_update_loop, args=(scheduler,))
    update_loop_thread.daemon = True
    update_loop_thread.start()
    CronsterSchedulerPrompt(scheduler).cmdloop(
        '{logo}\nWelcome to Cronster...'.format(logo=CRONSTER))


@click.command()
@click.option(
    '-h', '--cache-host', default='localhost',
    help='Cache host, default: localhost')
@click.option(
    '-p', '--cache-port', type=int, default=6379,
    help='Cache port, default: 6379 (Redis default)')
def cli(cache_host, cache_port):
    run_scheduler(cache_host, cache_port)


if __name__ == '__main__':
    cli()
