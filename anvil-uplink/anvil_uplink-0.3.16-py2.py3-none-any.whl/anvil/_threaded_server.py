# Helpers for implementing anvil.server on a threaded Real Python process.
# Used in uplink and downlink, but not in pypy-sandbox.

import threading, random, string, json, re, sys, time, importlib

from . import  _serialise, _server
from ._server import LazyMedia, registrations

string_type = str if sys.version_info >= (3,) else basestring

console_output = sys.stdout

class HttpRequest(threading.local):

    def __init__(self):
        self._prevent_access = True

    def __getattribute__(self, name):
        if threading.local.__getattribute__(self, "_prevent_access"):
            raise Exception("anvil.server.request is only available in http_endpoint calls.")

        return threading.local.__getattribute__(self, name)

_server.api_request = HttpRequest()

def _gen_id():
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))


# Overwrite with functions from context
send_reqresp = None


class LocalCallInfo(threading.local):
    def __init__(self):
        self.stack_id = None
        self.session = None
        self.cache_filter = {}
        self.cache_update = {}

    def __getitem__(self, item):
        return self.session.__getitem__(item)

    def __setitem__(self, key, value):
        return self.session.__setitem__(key, value)

    def __delitem__(self, key):
        del self.session[key]

    def get(self, key, default=None):
        return self.session.get(key, default)

    def __iter__(self):
        return self.session.__iter__()

    def __repr__(self):
        return "<Session:%s>" % repr(self.session)


call_info = LocalCallInfo()
call_responses = {}
waiting_for_calls = threading.Condition()

backends = {}


class IncomingRequest(_serialise.IncomingReqResp):
    def __init__(self, json, modules_to_import=None):
        self.modules_to_import = modules_to_import or []
        _serialise.IncomingReqResp.__init__(self, json)

    def execute(self):
        def make_call():
            call_info.stack_id = self.json.get('call-stack-id', None)
            sjson = self.json.get('sessionData', {'session': None, 'objects': []})
            call_info.session = _server._reconstruct_objects(sjson, None).get("session", {})
            call_info.enable_profiling = self.json.get('enable-profiling', False)
            if call_info.enable_profiling:
                call_info.profile = {
                    "origin": "Server (Python)",
                    "description": "Python _threaded_server execution",
                    "start-time": time.time()*1000,
                }
            call_info.cache_filter = _server.get_liveobject_cache_filter_spec([self.json['args'], self.json['kwargs']])
            call_info.cache_update = {}
            try:
                for n in self.modules_to_import:
                    importlib.import_module(n)

                if 'liveObjectCall' in self.json:
                    loc = self.json['liveObjectCall']
                    spec = dict(loc)

                    if self.json["id"].startswith("server-"):
                        spec["source"] = "server"
                    elif self.json["id"].startswith("client-"):
                        spec["source"] = "client"
                    else:
                        spec["source"] = "UNKNOWN"

                    del spec["method"]
                    backend = loc['backend']
                    if backend not in backends:
                        raise Exception("No such LiveObject backend: " + repr(backend))
                    inst = backends[backend](spec)
                    method = getattr(inst, loc['method'])

                    call_info.cache_filter.setdefault(backend, set()).add(spec['id'])

                    response = method(*self.json['args'], **self.json['kwargs'])
                else:
                    command = self.json['command']
                    for reg in registrations:
                        m = re.match(reg, command)
                        if m and len(m.group(0)) == len(command):
                            response = registrations[reg](*self.json["args"], **self.json["kwargs"])
                            break
                    else:
                        raise _server.NoServerFunctionError({'type': 'anvil.server.NoServerFunctionError',
                                                             'message': 'No server function matching "%s" has been registered' % command})


                def err(*args):
                    raise Exception("Cannot save DataMedia objects in anvil.server.session")

                try:
                    sjson = _server.fill_out_media({'session': call_info.session}, err)
                    json.dumps(sjson)
                except TypeError as e:
                    raise _server.SerializationError("Tried to store illegal value in a anvil.server.session. " + e.args[0])
                except _server.SerializationError as e:
                    raise _server.SerializationError("Tried to store illegal value in a anvil.server.session. " + e.args[0])

                resp = {"id": self.json["id"], "response": response, "sessionData": sjson, "cacheUpdates": call_info.cache_update}
                if call_info.enable_profiling:
                    call_info.profile["end-time"] = time.time()*1000
                    resp["profile"] = call_info.profile

                try:
                    send_reqresp(resp)
                except _server.SerializationError as e:
                    raise _server.SerializationError("Cannot serialize return value from function. " + str(e))
            except:
                e = _server._report_exception(self.json["id"])
                try:
                    send_reqresp(e)
                except:
                    trace = "\ncalled from ".join(["%s:%s" % (t[0], t[1]) for t in e["error"]["trace"]])
                    console_output.write(("Failed to report exception: %s: %s\nat %s\n" % (e["error"]["type"], e["error"]["message"], trace)).encode("utf-8"))
                    console_output.flush()
            finally:
                self.complete()

        threading.Thread(target=make_call).start()

    def complete(self):
        pass


class IncomingResponse(_serialise.IncomingReqResp):
    def execute(self):
        id = self.json['id']
        if id in call_responses:
            call_responses[id] = self.json
            with waiting_for_calls:
                waiting_for_calls.notifyAll()
        else:
            print("Got a response for an unknown ID: " + repr(self.json))


def kill_outstanding_requests(msg):
    for k in call_responses.keys():
        if call_responses[k] is None:
            call_responses[k] = {'error': {'message': msg}}

    with waiting_for_calls:
        waiting_for_calls.notifyAll()


# can be used as a decorator too
def register(fn, name=None):

    if isinstance(fn, str):
        # Someone's using the old syntax. Our bad.
        (fn, name) = (name, fn)

    if name is None:
        name = fn.__name__

    registrations[name] = fn

    if _server.on_register is not None:
        _server.on_register(name, False)

    def reregister(new_f):
        registrations[name] = new_f
        new_f._anvil_reregister = reregister

    fn._anvil_reregister = reregister

    return fn


def callable(fn_or_name=None):
    if fn_or_name is None or isinstance(fn_or_name, string_type):
        return lambda f: register(f, fn_or_name)
    else:
        return register(fn_or_name)


def register_live_object_backend(cls):

    name = "uplink." + cls.__name__
    backends[name] = cls

    if _server.on_register is not None:
        _server.on_register(name, True)

    return cls


live_object_backend = register_live_object_backend


# A parameterised decorator
def callable_as(name):
    print("@callable_as is deprecated. Please use @callable directly.")
    return lambda f: register(f, name)


def do_call(args, kwargs, fn_name=None, live_object=None): # Yes, I do mean args and kwargs without *s
    id = _gen_id()

    call_responses[id] = None

    profile = {
        "origin": "Server (Python)",
        "description": "Outgoing call from Python _threaded_server",
        "start-time": time.time()*1000
    }
    with waiting_for_calls:
        #print("Call stack ID = " + repr(_call_info.stack_id))
        if call_info.stack_id is None:
            call_info.stack_id = "outbound-" + _gen_id()
        req = {'type': 'CALL', 'id': id, 'args': args, 'kwargs': kwargs,
               'call-stack-id': call_info.stack_id}

        if live_object:
            req["liveObjectCall"] = dict(live_object._spec)
            req["liveObjectCall"]["method"] = fn_name
        elif fn_name:
            req["command"] = fn_name
        else:
            raise Exception("Expected one of fn_name or live_object")
        try:
            send_reqresp(req)
        except _server.SerializationError as e:
            raise _server.SerializationError("Cannot serialize arguments to function. " + str(e))

        while call_responses[id] is None:
            waiting_for_calls.wait()

    profile["end-time"] = time.time()*1000

    r = call_responses.pop(id)

    if "cacheUpdates" in r:
        # Apply updates to any of our own objects that were passed in
        _server.apply_cache_updates(r['cacheUpdates'], [args, kwargs, live_object])
        # Queue up whichever updates *we* should be returning
        _server.combine_cache_updates(call_info.cache_update, r['cacheUpdates'], call_info.cache_filter)

    if "profile" in r:
        profile["children"] = [r["profile"]]

    if hasattr(call_info, "profile"):
        if "children" not in call_info.profile:
            call_info.profile["children"] = []

        call_info.profile["children"].append(profile)

    if 'response' in r:
        return r['response']
    if 'error' in r:
        raise _server._deserialise_exception(r["error"])
    else:
        raise Exception("Bogus response from server: " + repr(r))
