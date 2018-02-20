from .bus import Bus
from .event import Event
from .decorators import listen_decorator

evntbus = Bus()
listen = listen_decorator(evntbus)
