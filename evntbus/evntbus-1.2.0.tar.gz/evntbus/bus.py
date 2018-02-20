import typing

from evntbus.event import Event


class Bus:
    def __init__(self):
        self.listeners = {}

    def reset(self):
        self.listeners = {}

    def listen(self, event: typing.Type, listener: typing.Callable,
               priority: int = 5):
        name = self._get_event_name(event)
        if name not in self.listeners:
            self.listeners[name] = {}
        if priority not in self.listeners[name]:
            self.listeners[name][priority] = []
        self.listeners[name][priority].append(listener)

    def emit(self, event: Event):
        name = self._get_event_name(type(event))
        if name not in self.listeners:
            return
        priorities = list(self.listeners[name].keys())
        priorities.sort(reverse=True)

        print('HERE', priorities)
        for priority in priorities:
            for listener in self.listeners[name][priority]:
                listener(event)

    @staticmethod
    def _get_event_name(event: typing.Type) -> str:
        return '.'.join([event.__module__, event.__name__])
