from queue import Queue, LifoQueue

from crawlster.helpers.base import BaseHelper


class QueueHelper(BaseHelper):
    """Helper for managing the task queue.

    It is required for a crawler to function
    """

    def __init__(self, strategy='fifo'):
        """Initializes the queue based on the given strategy

        Args:
            strategy (str):
                One of 'fifo' or 'lifo'. If ``'fifo'``, a queue will be used.
                If ``'lifo'``, a stack will be used.
        """
        super(QueueHelper, self).__init__()
        if strategy == 'fifo':
            self.queue = Queue()
        elif strategy == 'lifo':
            self.queue = LifoQueue()

    def put(self, item):
        """Puts an item to the queue"""
        self.queue.put(item)

    def get(self):
        """Returns the next item from the queue. Blocks if none is available"""
        return self.queue.get()

    def get_nowait(self):
        """Returns the next item from queue.

        Raises queue.EmptyQueue if no items are available
        """
        return self.queue.get_nowait()

    def join(self):
        """Waits until all jobs are processed"""
        self.queue.join()

    def task_done(self):
        """Marks a task as being done"""
        self.queue.task_done()
