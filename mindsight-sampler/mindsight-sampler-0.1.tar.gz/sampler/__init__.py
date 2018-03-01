import json
import requests, requests.exceptions
import signal


s = None

def start(server_url, interval=0.01, cache_depth=10000):
    global s
    if s is not None:
        s._enabled = True
        s.start()
        return

    s = Sampler(server_url, interval=interval, cache_depth=cache_depth)
    s.start()


def stop():
    global s
    s._enabled = False


class Sampler(object):
    def __init__(self, server_url, interval=0.01, cache_depth=10000):
        self.server_url = server_url
        self.interval = interval
        self.cache_depth = cache_depth
        self._cache = []
        self._enabled = True


    def _sample(self, signum, frame):
        if not self._enabled:
            return

        stack = []
        while frame is not None:
            formatted_frame = '{}.{}'.format(frame.f_globals.get('__name__'),
                frame.f_code.co_name)
            stack.insert(0, formatted_frame)
            frame = frame.f_back

        self._cache.append(stack)

        if len(self._cache) >= self.cache_depth:
            self._send_samples()

        signal.setitimer(signal.ITIMER_VIRTUAL, self.interval, 0)


    def _send_samples(self):
        try:
            url = "{}/samples/".format(self.server_url)
            h = {"Content-type": "application/json"}
            data = json.dumps(self._cache)
            r = requests.post(url, headers=h, data=data, timeout=0.001)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)

        self._cache = []


    def start(self):
        signal.signal(signal.SIGVTALRM, self._sample)
        signal.setitimer(signal.ITIMER_VIRTUAL, self.interval, 0)
