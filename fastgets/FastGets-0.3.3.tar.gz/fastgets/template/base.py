# coding: utf8

from .. import env
from ..core.log import logger
from ..core.errors import FrameError
from ..core import mode_parse


class TemplateBase(object):

    # thread_num
    # second_rate_limit
    # max_pending_task_num
    config = {}

    @classmethod
    def load(cls):
        raise NotImplementedError

    @classmethod
    def check_config(cls):
        for key, val in cls.config.items():
            if key not in ['thread_num', 'second_rate_limit', 'max_pending_task_num']:
                raise ValueError('unknown config item: {}'.format(key))

            if key == 'thread_num':
                if not isinstance(val, int) or not (10 >= val > 0):
                    raise ValueError('config thread_num must be int & 10 > thread_num > 0')
            if key == 'second_rate_limit':
                if not isinstance(val, int) or not val > 0:
                    raise ValueError('config second_rate_limit must be int & second_rate_limit > 0')
            if key == 'max_pending_task_num':
                if not isinstance(val, int) or not 100000 > val > 0:
                    raise ValueError('config max_pending_task_num must be int & 100,000 > max_pending_task_num > 0')

    @classmethod
    def run(cls):
        mode_parse()

        from ..engine import DistributedEngine, LocalEngine

        cls.check_config()

        if env.mode == env.TEST:
            engine = LocalEngine(cls, is_testing=True)
        elif env.mode == env.LOCAL:
            engine = LocalEngine(cls)
        elif env.mode == env.DISTRIBUTED:
            if not env.configured:
                raise ValueError('must call fastgets.init_fastgets_env to init env')
            engine = DistributedEngine(cls)
        else:
            raise FrameError('unknown mode')

        engine.run()
