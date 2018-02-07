'''Data Bench Transaction Scheduler

'''

import sched

class TransactionScheduler(object):
    '''
    '''
    def __init__(self, func, source):
        '''
          func: callable with one argument
        source: callable whose output is the argument to func

        '''
        self.scheduler = sched.scheduler()
        self.func      = func
        self.source    = source

    def schedule_transactions(self, schedule, batch_size, pri=1):
        '''
        schedule   : list of numbers, float OK
        batch_size : integer 
        pri        : optional integer priority, default 1

        Schedules invocations of TransactionSource objects using the
        schedule list passed in. The batch_size argument breaks up
        the schedule into equal batch_size segments, where batch_size
        invocations occur for each scheduling quanta.

        Returns an array of event IDs which can be used to remove
        the events from TransactionScheduler.scheduler. In practice,
        this may not be useful.
        '''
        
        def invocation():
            for n in range(batch_size):
                self.func(self.source())
            
        return [self.scheduler.enter(dt, pri, invocation) for dt in schedule]

    def run(self, transactions_per_second, seconds=-1, batch_sz=100):
        '''
        transactions_per_second : integer
        seconds                 : optional integer, defaults to -1
        batch_sz                : optional integer, defaults to 100

        Calls the configured func method using the configured 
        TransactionSource descended object as the argument, attempting
        to satisfy the requested number of transactions per second.

        '''
        batches = max(int(transactions_per_second / batch_sz), 1)
        scheduling_interval = 1/batches
        schedule = [scheduling_interval * (n+1) for n in range(batches)]
        while seconds:
            self.schedule_transactions(schedule, batch_sz)
            self.scheduler.run()
            seconds -= 1
