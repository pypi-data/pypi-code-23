import calendar
from haydn.event_emitter import event_emitter
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from threading import Timer
import time
import logging
from haydn.event_emitter import EventEmitter

__author__ = 'leemin'


class Scheduler(EventEmitter):

    schedule_list = None
    schedule_execution_list = None
    before_schedule_handler = None
    after_schedule_handler = None
    on_schedule_handler = None
    watch = None
    timer_interval = 1  # in second
    index = 0

    def __init__(self, timer_interval=1, tag=None):
        self.timer_interval = timer_interval
        self.watch = Watch(self.timer_interval)
        self.watch.on('tictoc',self.check_schedule)
        self.schedule_list = []
        self.schedule_execution_list = []
        self.before_schedule_handler = []
        self.after_schedule_handler = []
        self.on_schedule_handler = []
        self.tag = tag if tag is not None else 'schdeuler'+str(Scheduler.index)
        Scheduler.index+=1

        logging.debug('scheduler({}) initialized'.format(self.tag))

        pass

    def add_schedule(self, schedule, options=None):

        now = datetime.utcnow().replace(tzinfo=timezone.utc)

        if now > schedule.schedule_time.start_datetime:
            if schedule.schedule_time.repeat == ScheduleTime.REPEAT_NO:
                logging.warning('scheduled time is already passed : {}'.format(schedule.__str__()))
                return
            else:
                while now > schedule.schedule_time.start_datetime:
                    schedule.schedule_time.start_datetime = self.next_time(schedule)

        if schedule.schedule_time.end_datetime is not None and schedule.schedule_time.end_datetime <= now:
            logging.debug('{} - schedule ended : {}'.format(self.tag, schedule.__str__()))
            return

        schedule.status = Status.Waiting
        self.schedule_list.append(schedule)
        self.schedule_execution_list.append(schedule)
        logging.debug('{} - schedule added  : {}'.format(self.tag, schedule.__str__()))

    def remove_schedule(self, schedule):
        self.schedule_list.remove(schedule)
        self.schedule_execution_list.remove(schedule)
        logging.debug('{} - schedule removed  : {}'.format(self.tag, schedule.__str__()))

    def remove_all_schedules(self):
        self.schedule_list = []
        self.schedule_execution_list = []
        logging.debug('{} - all schedules are removed'.format(self.tag))

    def add_before_schedule_handler(self, handler):
        self.before_schedule_handler.append(handler)

    def add_after_schedule_handler(self, handler):
        self.after_schedule_handler.append(handler)

    def add_on_schedule_handler(self, handler):
        self.on_schedule_handler.append(handler)

    def start(self):
        # start its timer and check schedule to execute using check_schedule
        self.watch.start()
        pass

    def check_schedule(self):
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        for schedule in self.schedule_execution_list:
            if schedule.schedule_time.start_datetime <= now:
                logging.debug('{}: schedule on time. {}, {}'.format(self.tag, schedule, self))

                self.fire("schedule_on_time", schedule)
                schedule.status = Status.Doing

                try:
                    self.schedule_execution_list.remove(schedule)
                except ValueError:
                    logging.debug('{} - schedule already removed.'.format(self.tag))


                if schedule.task_params is not None:
                    schedule.task(*(schedule.task_params))
                else:
                    schedule.task()

                schedule.status = Status.Done
                self.fire("schedule_finished", schedule)

                schedule.repeat_count += 1

                if 0 < schedule.schedule_time.repeat_limit <= schedule.repeat_count:
                    logging.debug('{} - reached schedule repeat limit : {}'.format(self.tag, schedule.__str__()))
                    continue

                self.process_repeat(schedule)

    def process_repeat(self, schedule):
        logging.debug('{} - process schedule repeat  : {}'.format(self.tag, schedule.__str__()))

        if schedule.schedule_time.repeat == ScheduleTime.REPEAT_NO:
            logging.debug('{} - no repeat.'.format(self.tag))
            schedule.status = Status.Done
            return

        schedule.schedule_time.start_datetime = self.next_time(schedule)
        self.add_schedule(schedule)

    def next_time(self, schedule):
        current_datetime = schedule.schedule_time.start_datetime
        repeat = schedule.schedule_time.repeat
        repeat_interval = schedule.schedule_time.repeat_interval

        if repeat == ScheduleTime.REPEAT_NO:
            return current_datetime
        elif repeat == ScheduleTime.REPEAT_YEARLY:
            return current_datetime+timedelta(days=365 * repeat_interval)
        elif repeat == ScheduleTime.REPEAT_MONTHLY:
            return self.__add_months(current_datetime, repeat_interval)
        elif repeat == ScheduleTime.REPEAT_WEEKLY:
            return current_datetime + timedelta(weeks=repeat_interval)
        elif repeat == ScheduleTime.REPEAT_DAILY:
            return current_datetime + timedelta(days=repeat_interval)
        elif repeat == ScheduleTime.REPEAT_WEEKDAYS:
            return current_datetime + timedelta(days=repeat_interval)
        elif repeat == ScheduleTime.REPEAT_DAY:
            return current_datetime + timedelta(weeks=repeat_interval)
        elif repeat == ScheduleTime.REPEAT_HOURLY:
            return current_datetime + timedelta(hours=repeat_interval)
        elif repeat == ScheduleTime.REPEAT_MINUTELY:
            return current_datetime + timedelta(minutes=repeat_interval)
        elif repeat == ScheduleTime.REPEAT_SECOND:
            return current_datetime + timedelta(seconds=repeat_interval)

    def __add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)

    def remove_schedule_by_reference_id(self, reference_id):
        removed = None
        for schedule in self.schedule_execution_list:
            if schedule.reference_id == reference_id:
                removed=schedule;
                self.schedule_execution_list.remove(schedule)
        for schedule in self.schedule_list:
            if schedule.reference_id == reference_id:
                self.schedule_list.remove(schedule)
        logging.debug('{} - schedule removed by reference id : {}'.format(self.tag, removed.__str__()))


class ScheduleTime:
    REPEAT_YEARLY = "repeat_yearly"
    REPEAT_MONTHLY = "repeat_monthly"
    REPEAT_WEEKLY = "repeat_weekly"
    REPEAT_DAILY = "repeat_daily"
    REPEAT_HOURLY = "repeat_hourly"
    REPEAT_MINUTELY = "repeat_minutely"
    REPEAT_SECOND = "repeat_second"
    REPEAT_DAY = "repeat_day"
    REPEAT_WEEKDAYS = "repeat_weekdays"
    REPEAT_NO = "repeat_no"
    repeat = REPEAT_NO
    repeat_interval = 1

    start_datetime = None
    end_datetime = None

    def __init__(self, start_datetime, end_datetime=None, repeat=REPEAT_NO, repeat_interval=1, repeat_limit=0):
        if repeat_interval == 0:
            repeat_interval = 1

        self.start_datetime = start_datetime.astimezone(tz=timezone.utc) if start_datetime.tzinfo is not None else start_datetime.replace(tzinfo=timezone.utc)

        if end_datetime is not None:
            self.end_datetime = end_datetime.astimezone(tz=timezone.utc) if end_datetime.tzinfo is not None else end_datetime.replace(tzinfo=timezone.utc)
        self.repeat = repeat if repeat is not None else self.REPEAT_NO
        self.repeat_interval = repeat_interval
        self.repeat_limit = repeat_limit

    def __str__(self):
        return '{}, repeat option: {}, repeat interval: {}'.format((self.start_datetime-timedelta(seconds=time.timezone)).strftime("%Y-%m-%d %H:%M:%S"), self.repeat, self.repeat_interval, self.repeat_limit)


class Status:
    Ready = 'Ready'
    Canceled = 'Canceled'
    Doing = 'Doing'
    Done = 'Done'
    Waiting = 'Waiting'


class Schedule:
    task = None
    time = None
    options = {
    }
    task_params = None
    reference_id = None
    repeat_count = 0
    status = Status.Ready

    def __init__(self, schedule_time, task, options=None, task_params=None, reference_id=None):
        self.schedule_time = schedule_time
        self.task = task
        self.task_params = task_params
        if options is not None:
            self.options = options
        self.reference_id = reference_id

        return

    def __str__(self):
        return 'schedule_time :{} ,schedule options: {},reference_id: {},repeat_count: {}'.format(self.schedule_time.__str__(), self.options, self.reference_id.__str__(), self.repeat_count.__str__())


class Watch(EventEmitter):
    def __init__(self, t):
        self.t = t
        self.thread = Timer(self.t, self.handle_function)

    def handle_function(self):
        self.fire('tictoc')
        self.thread = Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()
