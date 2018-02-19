import multiprocessing as mp
import os


class AsyncDistributor(object):

    def __init__(self, n_workers=None, worker_engine=None):
        self.n_worker = n_workers or os.cpu_count() * 2
        self.worker_engine = worker_engine or str
        self.ctx = mp.get_context('spawn')
        self.communication = {}
        self.workers = {}
        self.workers_manager = None
        self.workers_consumer = None

        self.prepare_workers()
        self.run()

    def prepare_workers(self):
        for i in range(self.n_worker):
            parent_conn, worker_conn = self.ctx.Pipe()
            self.communication[i] = {
                'parent': parent_conn,
                'worker': worker_conn,
            }

        self.communication['output'] = self.ctx.Queue()
        self.communication['logger'] = self.ctx.Queue()
        self.communication['ready'] = self.ctx.Queue()
        self.communication['tasks'] = self.ctx.Queue()

    def run(self):
        for i in range(self.n_worker):
            p = self.ctx.Process(target=AsyncDistributor.worker_engine, args=(i, self.communication, self.worker_engine))
            self.workers[i] = p
        for p in self.workers.values():
            p.start()

        self.workers_manager = self.ctx.Process(target=AsyncDistributor.worker_manager_engine, args=(self.communication,))
        self.workers_manager.start()

    @staticmethod
    def worker_engine(_id, communication, worker_engine):
        print('worker {} ready'.format(_id))
        worker_comm = communication[_id]['worker']
        communication['ready'].put(_id)
        while True:
            task = worker_comm.recv()
            result = worker_engine(task)
            print(_id, result)
            communication['output'].put(result)
            communication['ready'].put(_id)

    @staticmethod
    def worker_manager_engine(communication):
        ready = communication['ready']
        tasks = communication['tasks']

        while True:
            task = tasks.get()
            worker = ready.get()
            communication[worker]['parent'].send(task)

    def submit(self, item):
        self.communication['tasks'].put(item)

    def valid_output(self):
        return not self.communication['output'].empty()

    def output(self):
        if not self.communication['output'].empty():
            result = self.communication['output'].get()
            return result
        return None

    def output_block(self):
        result = self.communication['output']
        return result
