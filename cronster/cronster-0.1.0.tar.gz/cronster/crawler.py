#!/usr/bin/env python
import os
import glob
import json
import time
import hashlib
from datetime import datetime

import yaml
import click
import redis
from tabulate import tabulate


class CronsterCrawler(object):
    """
    Cronster crawler class. Crawl the file system recursively for ``crontab``
    files, read the contents and store a list of
    :class:`~cronster.scheduler.CronsterJob` in a Redis cache.
    """
    def __init__(self, root, cache_host, cache_port, interval):
        """
        Initialise a :class:`~cronster.crawler.CronsterCrawler`.

        :param root: File system root to crawl
        :type root: str
        :param cache_host: Host that serves the Redis cache
        :type cache_host: str
        :param cache_port: Port on the host that exposes the Redis service
        :type cache_port: int
        :param interval: Time between crawls in seconds
        :type interval: int
        """
        if not os.path.exists(root):
            raise OSError('Root does not exist')
        self.root = root
        os.chdir(self.root)
        self.cache = redis.StrictRedis(
            host=cache_host, port=cache_port, db=0, decode_responses=True)
        self.interval = interval

    def get_crontab_data(self, crontab):
        """
        Given a ``crontab`` file path, load and return the
        :class:`~cronster.scheduler.CronsterJob` contained in
        the file.

        :param crontab: Crontab file path
        :type crontab: str
        :return: Jobs
        :rtype: list

        Example output:

        .. code-block:: json

            [
                {
                    "name": "job_name",
                    "cmd": "echo $PATH",
                    "schedule": "* * * * *",
                    "path": "/path/to/crontab/file",
                    "hash": "dc8a776c99d9b8ab97550e87c857dc959a857c5b"
                }
            ]
        """
        with open(crontab, 'r') as fp:
            crontab_data = yaml.load(fp)
        jobs = []
        for job_name, job_data in crontab_data.items():
            job = {}
            job_hash = hashlib.sha1()
            job['path'] = crontab
            job_hash.update(crontab.encode('ascii'))
            job['name'] = job_name
            job_hash.update(job_name.encode('ascii'))
            for key, value in job_data.items():
                job[key] = value
                job_hash.update(value.encode('ascii'))
            job['hash'] = job_hash.hexdigest()
            jobs.append(job)
        return jobs

    def crawl(self):
        """
        Recursively crawl the file system from ``root`` in a given
        ``interval``. Add :class:`~cronster.scheduler.CronsterJob` from
        ``crontab`` files to the cache as a JSON string.
        """
        while True:
            self.crontabs = []
            for crontab in glob.glob('**/crontab', recursive=True):
                self.crontabs += self.get_crontab_data(crontab)
            self.cache.set('cronster_crawler', json.dumps(self.crontabs))
            self.display_crontabs()
            time.sleep(self.interval)

    def display_crontabs(self):
        """
        Print the current cache content to the console in tabulated form.
        """
        crontab_data = json.loads(self.cache.get('cronster_crawler'))
        click.clear()
        metadata = [
            [
                'Cronster Crawler'
            ],
            [
                'Crawler time: ',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        ]
        print(tabulate(metadata))
        print('\n')
        headers = ['Job Name', 'Hash', 'Schedule']
        job_data = []
        for job in sorted(crontab_data, key=lambda x: x['name']):
            job_data.append([job['name'], job['hash'], job['schedule']])
        print(tabulate(job_data, headers=headers))

    def __repr__(self):
        return '<CronsterCrawler>'

    def __str__(self):
        return str({
            'root': self.root,
            'cache_host': self.cache_host,
            'cache_port': self.cache_port,
            'interval': self.interval
        })


@click.command()
@click.option(
    '-r', '--root', default=os.getcwd(),
    help='Crawling root, default: the current working directory')
@click.option(
    '-h', '--cache-host', default='localhost',
    help='Cache host, default: localhost')
@click.option(
    '-p', '--cache-port', type=int, default=6379,
    help='Cache port, default: 6379 (Redis default)')
@click.option(
    '-i', '--interval', type=int, default=2,
    help='Crawling interval, default: 2 seconds')
def cli(root, cache_host, cache_port, interval):
    crawler = CronsterCrawler(root, cache_host, cache_port, interval)
    crawler.crawl()


if __name__ == '__main__':
    cli()
