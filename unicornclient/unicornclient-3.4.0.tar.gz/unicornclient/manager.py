# pylint: disable=W0122

import os
import logging
import threading

from . import config
from . import routine

class SupervisionException(Exception):
    pass
class StopRoutineException(Exception):
    pass

class Manager(object):
    def __init__(self, sender):
        logging.info('creating manager')
        self.sender = sender
        self.threads = {}

    def start_default(self):
        self.start_routines(config.DEFAULT_ROUTINES)

    def start_routines(self, routines):
        for routine_name in routines:
            if not routine_name in self.threads:
                self.start_routine(routine_name)

    def start_routine(self, name, code=None):
        if not name:
            raise SupervisionException("trying to start routine with no name")

        if name in self.threads:
            try:
                self.stop_routine(name)
            except StopRoutineException:
                raise SupervisionException('could not stop routine')

        if not code:
            code = self.__find_code(name)

        if not code:
            raise SupervisionException('no code for ' + name)

        logging.info("starting routine %s", name)
        context = {}
        exec(code, context)

        user_routine_class = self.__find_subclass(context)
        if not user_routine_class:
            raise SupervisionException('no routine subclass defined in code for ' + name)

        user_routine = user_routine_class()
        user_routine.manager = self
        user_routine.daemon = True
        user_routine.start()
        self.threads[name] = user_routine

    def stop_routine(self, name):
        logging.info('stopping routine %s', name)
        if threading.current_thread() == self.threads[name]:
            raise StopRoutineException('routine can not stop itself')

        running_routine = self.threads[name]
        running_routine.stop_signal()
        running_routine.join()
        del self.threads[name]

        logging.info('routine %s stopped', name)

    def __find_code(self, name):
        routine_path = os.path.join(os.path.dirname(__file__), 'routines', name + '.py')
        try:
            with open(routine_path, 'r') as routine_file:
                return routine_file.read()
        except FileNotFoundError as err:
            logging.error(err)
            return None

    def __find_subclass(self, context):
        for key in context:
            try:
                if issubclass(context[key], routine.Routine):
                    return context[key]
            except TypeError:
                pass
        return None

    def join(self):
        for thread in self.threads.values():
            thread.join()

    def forward(self, name, task):
        if name == 'routine':
            try:
                routine_name = task['name'] if 'name' in task else None
                routine_code = task['code'] if 'code' in task else None
                self.start_routine(routine_name, routine_code)
            except SupervisionException as err:
                logging.warning(err)
            return

        if name in self.threads:
            self.threads[name].queue.put(task)
            return

    def send(self, message):
        self.sender.send(message)

    def authenticate(self):
        self.forward('auth', {'action':'authenticate'})
