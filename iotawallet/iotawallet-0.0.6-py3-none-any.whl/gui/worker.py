import queue
import traceback
import threading
from typing import Callable, Optional, Tuple

import wx

QueueType = Tuple[Callable, Tuple, Optional[Callable]]


class WorkerThread:
    def __init__(self) -> None:
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.queue: queue.Queue[QueueType] = queue.Queue()
        self.thread.start()

    def _run(self) -> None:
        while True:
            command, args, callback = self.queue.get()
            try:
                result = command(*args)
                if callback:
                    wx.CallAfter(callback, result)
            except Exception as e:
                traceback.print_exc()

    def send(self,
             command: Callable,
             args: Tuple = (),
             callback: Optional[Callable] = None) -> None:
        self.queue.put((command, args, callback))
