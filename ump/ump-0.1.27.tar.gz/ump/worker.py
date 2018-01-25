# coding: utf8


"""
工作者
获取远端的数据，并进行处理。
默认使用redis队列
"""

import sys
import redis
import os
import setproctitle
import copy
import subprocess
import time
import thread
import signal

import constants
from log import logger


class Worker(object):

    # 是否有效(父进程中代表程序有效，子进程中代表worker是否有效)
    enable = True
    # 子进程列表
    processes = None

    # 停止子进程超时(秒). 使用 TERM 进行停止时，如果超时未停止会发送KILL信号
    stop_timeout = None

    rds = None
    redis_key = None

    def __init__(self, redis_url, redis_key):
        self.processes = list()
        self.rds = redis.StrictRedis.from_url(redis_url)
        self.redis_key = redis_key

    def handle(self, data):
        # 必须继承
        raise NotImplementedError

    def run(self, workers=None):

        workers = workers if workers is not None else 1

        if os.getenv(constants.WORKER_ENV_KEY) != 'true':
            # 主进程
            logger.info('Run worker. redis_key: %s, workers: %s', self.redis_key, workers)

            # 设置进程名
            setproctitle.setproctitle(self._make_proc_name('master'))
            # 只能在主线程里面设置signals
            self._handle_parent_proc_signals()
            self._spawn_workers(workers)
        else:
            # 子进程
            setproctitle.setproctitle(self._make_proc_name('worker'))
            self._worker_run()

    def _spawn_workers(self, workers):
        """
        启动多个worker
        :param workers:
        :return:
        """
        worker_env = copy.deepcopy(os.environ)
        worker_env.update({
            constants.WORKER_ENV_KEY: 'true'
        })

        def start_worker_process():
            args = [sys.executable] + sys.argv
            try:
                return subprocess.Popen(args, env=worker_env)
            except:
                logger.error('exc occur. app: %s, args: %s, env: %s',
                             self, args, worker_env, exc_info=True)
                return None

        for it in xrange(0, workers):
            p = start_worker_process()
            self.processes.append(p)

        while 1:
            for idx, p in enumerate(self.processes):
                if p and p.poll() is not None:
                    # 说明退出了
                    self.processes[idx] = None

                    if self.enable:
                        # 如果还要继续服务
                        p = start_worker_process()
                        self.processes[idx] = p

            if not filter(lambda x: x, self.processes):
                # 没活着的了
                break

            # 时间短点，退出的快一些
            time.sleep(0.1)

    def _worker_run(self):
        self._handle_child_proc_signals()

        while self.enable:
            try:
                data = self.rds.blpop(self.redis_key, timeout=constants.REDIS_POP_TIMEOUT)
            except KeyboardInterrupt:
                return
            except:
                logger.error('redis blpop exc occur.', exc_info=True)
                # 等一下，可能服务器问题
                time.sleep(1)
                continue

            # logger.debug('data: %s', data)
            if not data:
                continue

            while True:
                try:
                    # 格式为 (key, item)
                    self.handle(data[1])
                    # 成功执行才能退出循环
                    break
                except:
                    logger.error('handle data exc occur. data: %r', data, exc_info=True)
                    time.sleep(1)

    def _make_proc_name(self, subtitle):
        """
        获取进程名称
        :param subtitle:
        :return:
        """
        proc_name = '[%s:%s %s] %s' % (
            constants.NAME,
            subtitle,
            self.redis_key,
            ' '.join([sys.executable] + sys.argv)
        )

        return proc_name

    def _handle_parent_proc_signals(self):
        def kill_processes_later(processes, timeout):
            """
            等待一段时间后杀死所有进程
            :param processes:
            :param timeout:
            :return:
            """
            def _kill_processes():
                # 等待一段时间
                time.sleep(timeout)

                for p in processes:
                    if p and p.poll() is None:
                        # 说明进程还活着
                        p.send_signal(signal.SIGKILL)

            thread.start_new_thread(_kill_processes, ())

        def stop_handler(signum, frame):
            """
            等所有子进程结束，父进程也退出
            """
            self.enable = False

            # 一定要这样，否则后面kill的时候可能会kill错
            processes = self.processes[:]

            # 如果是终端直接CTRL-C，子进程自然会在父进程之后收到INT信号，不需要再写代码发送
            # 如果直接kill -INT $parent_pid，子进程不会自动收到INT
            # 所以这里可能会导致重复发送的问题，重复发送会导致一些子进程异常，所以在子进程内部有做重复处理判断。
            for p in processes:
                if p:
                    p.send_signal(signum)

            if self.stop_timeout is not None:
                kill_processes_later(processes, self.stop_timeout)

        def safe_reload_handler(signum, frame):
            """
            让所有子进程重新加载
            """
            processes = self.processes[:]

            for p in processes:
                if p:
                    p.send_signal(signal.SIGHUP)

        # INT, QUIT为强制结束
        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGQUIT, stop_handler)
        # TERM为安全结束
        signal.signal(signal.SIGTERM, stop_handler)
        # HUP为热更新
        signal.signal(signal.SIGHUP, safe_reload_handler)

    def _handle_child_proc_signals(self):
        def stop_handler(signum, frame):
            # 防止重复处理KeyboardInterrupt，导致抛出异常
            if self.enable:
                self.enable = False
                raise KeyboardInterrupt

        def safe_stop_handler(signum, frame):
            self.enable = False

        # 强制结束，抛出异常终止程序进行
        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGQUIT, stop_handler)
        # 安全停止
        signal.signal(signal.SIGTERM, safe_stop_handler)
        signal.signal(signal.SIGHUP, safe_stop_handler)
