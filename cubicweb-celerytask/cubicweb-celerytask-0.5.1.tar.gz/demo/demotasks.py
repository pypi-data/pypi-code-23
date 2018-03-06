from __future__ import print_function

import sys
import logging
import time
import random

from celery import current_app as app
from celery import chord
from celery.utils.log import get_task_logger
from cw_celerytask_helpers.redislogger import redirect_stdouts

# 3 kinds of logger
cw_logger = logging.getLogger('cubes.tasks')
dummy_logger = logging.getLogger('dummy')
logger = get_task_logger(__name__)


@app.task(name='success')
def success(n):
    logger.info('TASK SUCCESS: (%s)', n)
    time.sleep(random.random()*2)
    return n


@app.task(name='fail')
def fail():
    logger.info('TASK FAIL')
    raise RuntimeError('fail')


@app.task(name='log')
def log():
    for out in [sys.stdout, sys.stderr]:
        print('should not be in logs', file=out)

    with redirect_stdouts(logger):
        print('out should be in logs')
        print('err should be in logs', file=sys.stderr)

    for out in [sys.stdout, sys.stderr]:
        print('should not be in logs', file=out)

    for name, l, state in [
        ('cw', cw_logger, 'be'),
        ('celery', logger, 'be'),
        ('dummy', dummy_logger, 'not be')
    ]:
        for key in ('debug', 'info', 'warning', 'error', 'critical'):
            getattr(l, key)('%s %s should %s in logs', name, key, state)
        try:
            raise RuntimeError("fail")
        except RuntimeError:
            l.exception('%s exception should be in logs', name)

    raise Exception("oops")


@app.task(name="add")
def add(x, y):
    logger.info('TASK ADD: (%s, %s)', x, y)
    return x + y


@app.task(bind=True, name="tsum")
def tsum(self, args, root_id=None):
    if root_id is None:
        root_id = self.request.id
    logger.info('TASK SUM: (%s) <root=%s>', len(args), root_id)
    return sum(args)


@app.task(bind=True, name='hi_there')
def my_task(self, arg, kw=0, root_id=None):
    if root_id is None:
        root_id = self.request.id
    logger.info('HI %s %s! <root=%s>', arg, kw, root_id)
    if kw is 'wait':
        time.sleep(1)
    return 42


@app.task(bind=True, name='show-me-progress')
def progress(self, steps=10):
    self.update_state(state='PROGRESS', meta={'progress': 0.0})
    for i in range(steps):
        val = random.random()*2
        logger.info('Step %s: going to sleep for %.2fs', i, val)
        time.sleep(val)
        self.update_state(state='PROGRESS',
                          meta={'progress': (i+1/steps)})


@app.task(bind=True, name='multi')
def multi(self):
    logger.info('Starting multi!')
    time.sleep(2)
    logger.info('Running subtasks!')
    r = chord([my_task.si(i, kw='wait') for i in range(5)],
              tsum.s())
    logger.info('multi done!')
    return r().serializable()
