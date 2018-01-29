# coding: utf8

from .time_counter import MinuteCounter, SecondCounter, DayCounter


class ClusterStats(object):

    @classmethod
    def add_thread(cls, thread_id, pipe=None):
        MinuteCounter.incr('thread', thread_id, pipe=pipe)

    @classmethod
    def add_server(cls, server_ip, pipe=None):
        MinuteCounter.incr('server', server_ip, pipe=pipe)

    @classmethod
    def incr(cls, name, pipe=None):
        # name: success crawl_error process_error retry lost
        SecondCounter.incr('cluster', name, pipe=pipe)
        DayCounter.incr('cluster', name, pipe=pipe)

    @classmethod
    def get_current_server_num(cls):
        return len(MinuteCounter.get_counts('server')[-1][-1])

    @classmethod
    def get_current_thread_num(cls):
        return len(MinuteCounter.get_counts('thread')[-1][-1])

    @classmethod
    def get_today_success_num(cls):
        return DayCounter.get_count('cluster', field='success')

    @classmethod
    def get_today_error_num(cls):
        return DayCounter.get_count('cluster', field='crawl_error') + \
               DayCounter.get_count('cluster', field='process_error')

    @classmethod
    def get_recent_stats(cls, num=60):
        return SecondCounter.get_counts('cluster', num=num)
