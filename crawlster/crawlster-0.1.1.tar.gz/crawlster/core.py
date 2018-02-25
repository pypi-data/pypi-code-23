import datetime
import queue
import threading
import time
import sys
import traceback

from crawlster.handlers.stream import StreamItemHandler
from crawlster.helpers.extract import ExtractHelper
from crawlster.helpers.log import LoggingHelper
from crawlster.helpers import UrlsHelper, RegexHelper
from crawlster.exceptions import get_full_error_msg, ConfigurationError
from crawlster.helpers.queue import QueueHelper
from crawlster.helpers.http.requests import RequestsHelper
from crawlster.helpers.stats import StatsHelper


def start(method):
    """Decorator for specifying the start step.

    Must decorate a single method from the crawler class"""
    method._crawlster_start_step = True
    return method


class JobTypes:
    FUNC = 'func'
    EXIT = 'exit'


class Job(object):
    """Base job class"""

    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return "Job(type={type})".format(type=self.type)


class FuncJob(Job):
    """Job used to tell the worker what to execute next"""

    def __init__(self, func, args, kwargs):
        super(FuncJob, self).__init__(JobTypes.FUNC)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "Job(type={}, func={}, args= {}, kwargs={})".format(
            self.type, self.func.__name__, self.args, self.kwargs
        )


class ExitJob(Job):
    """Job used to signal finishing the crawling to the workers"""

    def __init__(self):
        super(ExitJob, self).__init__(JobTypes.EXIT)


class Crawlster(object):
    """Base class for web crawlers

    Any crawler must subclass this and provide a valid Configuration object
    as the config class attribute.

    """
    # constants
    HELPER_FLAG = 'is_helper'
    # stats
    STAT_ITEMS = 'items'
    STAT_ERRORS = 'errors'
    STAT_START_TIME = 'time.start'
    STAT_FINISH_TIME = 'time.finish'
    STAT_DURATION = 'time.duration'

    # Helpers
    # =======
    # we directly attach them because we want the nice auto complete
    # features of IDEs

    # Core helpers. They must always be provided
    stats = StatsHelper()
    log = LoggingHelper()
    http = RequestsHelper()
    queue = QueueHelper(strategy='lifo')
    # other helpers
    urls = UrlsHelper()
    regex = RegexHelper()
    extract = ExtractHelper()

    # a single item handler or a list/tuple of them
    item_handler = StreamItemHandler()

    def __init__(self, config=None):
        """Initializes the crawler"""
        self.config = config
        if self.config is None:
            raise ConfigurationError(get_full_error_msg('missing_config'))

        self.pool = None
        self.populate_config()
        self.inject_helpers()
        self.inject_handlers()
        self.log.info('Initializing context')
        self.init_context()
        self.log.info('Context initialized')

    def inject_helpers(self):
        """Injects and initializes all the known helpers"""
        for helper in self.iter_helpers():
            self.inject_config_and_crawler(helper)

    def inject_handlers(self):
        """Injects and initializes all the known item handlers"""
        for handler in self.iter_item_handlers():
            self.inject_config_and_crawler(handler)

    def iter_helpers(self):
        """Iterates through all the item handlers"""
        for attrname in dir(self):
            attr_obj = getattr(self, attrname)
            if hasattr(attr_obj, self.HELPER_FLAG) and \
                    getattr(attr_obj, self.HELPER_FLAG):
                yield attr_obj

    def iter_item_handlers(self):
        """Iterates through all the known item handlers"""
        if isinstance(self.item_handler, (list, tuple)):
            for handler in self.item_handler:
                yield handler
        else:
            yield self.item_handler

    def inject_config_and_crawler(self, to_be_injected):
        """Injects the config instance and crawler instance into the object

        The crawler instance will be accessible through the .crawler attribute,
        the config instance will be accessible through the .config attribute.
        After injection, the .initialize() is called to perform the init
        actions.

        Args:
            to_be_injected (object which has initialize()):
                An object in which will be injected the config and crawler
                attributes. Must have an .initialize() method
        """
        to_be_injected.config = self.config
        to_be_injected.crawler = self
        to_be_injected.initialize()

    def init_context(self):
        """Initializes the crawler context (the queue and the worker pool)"""
        # prepare queue
        self.pool = self.get_pool()

    def get_pool(self):
        """Creates and returns the worker pool"""
        workers = self.config.get('core.workers')
        pool = []
        for _ in range(workers):
            pool.append(threading.Thread(target=self.worker))
        return pool

    def start(self):
        """Starts crawling based on the config"""
        self.stats.set(self.STAT_START_TIME, datetime.datetime.now())
        func = self.get_start_step()
        if not func:
            raise ConfigurationError('Could not find start step')
        start_urls = self.config.get('core.start_urls')
        # putting initial processing jobs into queue
        for start_url in start_urls:
            self.queue.put(FuncJob(func, (start_url,), {}))
        # start workers
        for worker_thread in self.pool:
            worker_thread.start()
        self.queue.join()
        self.log.info('Finished')
        self.log.debug('Signaling workers to stop')
        for _ in range(len(self.pool)):
            self.queue.put(ExitJob())
        # updating stats
        finish = datetime.datetime.now()
        self.stats.set(self.STAT_FINISH_TIME, finish)
        start = self.stats.get(self.STAT_START_TIME)
        duration = (finish - start).total_seconds()
        self.stats.set(self.STAT_DURATION, duration)
        self.finalize()

    def worker(self):
        """Worker body that executes the jobs"""
        work_queue = self.queue
        while True:
            try:
                job = work_queue.get_nowait()
            except queue.Empty:
                job = None
            if not job:
                time.sleep(0.2)
                continue
            self.log.debug('Got job: {}'.format(job))
            if job.type == JobTypes.EXIT:
                self.log.info('Received exit notification. Worker is exiting')
                work_queue.task_done()
                return
            self.process_job(job)
            work_queue.task_done()

    def process_job(self, job):
        """Processes a single job and enqueues the results"""
        self.log.debug('Processing job: {}'.format(job))
        try:
            next_item = job.func(*job.args, **job.kwargs)
        except Exception as e:
            self.report_error(e, job)
            self.stats.add(self.STAT_ERRORS, {
                'func': job.func.__name__,
                'args': job.args,
                'kwargs': job.kwargs,
                'exception': e
            })
            return
        if not next_item:
            return
        if isinstance(next_item, dict):
            # is an item/result
            self.submit_item(next_item)
        elif isinstance(next_item, Job):
            # is a job instance, must be further processes
            self.queue.put(next_item)

    def report_error(self, e, failed_job):
        """Reports a failed job

        Args:
            e (Exception):
                The exception instance that was thrown
            failed_job (Job):
                The job instance that caused the exception
        """
        self.log.error('Job failed: {}'.format(failed_job))
        exc_type, exc_instance, exc_tb = sys.exc_info()
        for line in traceback.format_exception(exc_type, exc_instance,
                                               exc_tb):
            self.log.error(line.rstrip())
        self.log.error(str(e))

    def finalize(self):
        """Performs the finalize action on all item handlers and helpers"""
        for handler in self.iter_item_handlers():
            handler.finalize()
        for helper in self.iter_helpers():
            helper.finalize()

    def populate_config(self):
        """Populates the config with the options from helpers and item handlers

        Each helper and item handler defines a list of options that it uses.
        This method will visit each helper and item handler to populate the
        config instance with those options.
        """
        for helper in self.iter_helpers():
            self.config.register_options(helper.config_options)
        for handler in self.iter_item_handlers():
            self.config.register_options(handler.config_options)

    # Workflow methods

    def schedule(self, func, *args, **kwargs):
        """Schedules the next tep to be executed by workers"""
        job = FuncJob(func, args, kwargs)
        self.queue.put(job)

    def submit_item(self, item):
        """Submit an item to be handled by the item handlers

        Args:
            item (dict):
                The item that has to be processed
        """
        self.log.debug('Submitted item {}'.format(item))
        self.stats.incr(self.STAT_ITEMS)
        if isinstance(self.item_handler, (list, tuple)):
            for handler in self.item_handler:
                handler.handle(item)
        else:
            self.item_handler.handle(item)

    def get_start_step(self):
        for attrname in dir(self):
            func = getattr(self, attrname)
            flag = '_crawlster_start_step'
            if callable(func) and hasattr(func, flag) and getattr(func, flag):
                return func
