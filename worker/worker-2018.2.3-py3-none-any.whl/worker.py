from worker.simple import work as simple_work
from worker.coroutine import work as coroutine_work
from worker.thread import work as thread_work
from worker.process import work as process_work

worker_map = {
    'simple': simple_work,
    'coroutine': coroutine_work,
    'thread': thread_work,
    'process': process_work
}


class Worker:
    def __init__(self, mode='thread'):
        self.mode = mode
        self.worker_func = worker_map.get(self.mode, thread_work)

    def work(self, data, info):
        return self.worker_func(data, info)



async def worker_do_sth(data, info):
# def worker_do_sth(data, info):
    print('>>', info, data)



if __name__ == '__main__':
    data = [
               {'test': '......'},
           ] * 90
    info = {
        'worker': 'worker.worker.worker_do_sth'
    }
    worker = Worker(mode='coroutine')
    # worker = Worker(mode='simple')
    # worker = Worker(mode='thread')
    # worker = Worker(mode='process')
    resp = worker.work(data, info)
    print(resp)
