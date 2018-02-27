from ladon.compat import PORTABLE_STRING
from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType
import time


class RetType(LadonType):
  a = int
  b = str

class TaskService(object):

    @ladonize(int, rtype=int, tasktype=True)
    def thrTaskExample(self, counter, **kw):
        """
        Use the built-in tasktype relying on the threading module
        @param counter: dummy param
        @param kw:
        @return:
        """
        set_progress = kw['update_progress']
        repeat = 30.0
        for i in range(int(repeat)):
            time.sleep(.5)
            set_progress(float(i+1.0)/repeat)
        return counter

    @ladonize(int, rtype=int, tasktype={"enable": True, "memcache_server": "127.0.0.1"})
    def mpTaskExample(self, counter, **kw):
        """
        Use third-party memcache system for communication and multiprocessing for execution.
        This method returns a basic data type.
        @param counter: dummy arg
        @param kw:
        @return:
        """
        set_progress = kw['update_progress']
        repeat = 30.0
        for i in range(int(repeat)):
            time.sleep(.5)
            set_progress(float(i+1.0)/repeat)
        return counter

    @ladonize(int, rtype=RetType, tasktype={"enable": True, "redis_server": "127.0.0.1"})
    def mpTaskExampleComplex(self, counter, **kw):
        """
        Use third-party redis system for communication and multiprocessing for execution.
        This method returns a LadonType data type.
        @param counter: dummy arg
        @param kw:
        @return:
        """
        set_progress = kw['update_progress']
        repeat = 30.0
        for i in range(int(repeat)):
            time.sleep(.5)
            set_progress(float(i+1.0)/repeat)
        r = RetType()
        r.a = counter
        r.b = 'Some nice text'
        return r

    @ladonize(rtype=bool)
    def lengthyCall(self):
        time.sleep(10)
        return True
