import typing

if typing.TYPE_CHECKING:
    from evntbus.bus import Bus


def listen_decorator(evntbus: 'Bus'):
    class ListenDecorator(object):
        def __init__(self, event: typing.Type, priority: int = 5):
            self.event = event
            self.priority = priority

        def __call__(self, f: typing.Callable) -> typing.Callable:
            evntbus.listen(self.event, f, self.priority)
            return f

    return ListenDecorator
