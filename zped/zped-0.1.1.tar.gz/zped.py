class ZPED:

    class StopExecution(Exception):
        """Raise this to stop the execution of a triggerman"""
        def __init__(self, result=None, trigger_post=True):
            self.result = result
            self.trigger_post = trigger_post

    class ModifyPayload(Exception):
        """Raise this to modify the payload passed along the call stack"""
        def __init__(self, *payload):
            self.payload = payload

    def __init__(self):
        self.__events__ = {}

    def _validate_event(self, event):
        if not event in self.__events__:
            raise NameError("`%s` is not a valid event for %s" % (event, self.__class__))

    def on(self, event, callback=None):
        """Registers a function as a callback. Can be used as a decorator."""
        self._validate_event(event)

        if not callback:
            # Assume we're being called as a decorator
            def decorator(callback):
                self.on(event, callback)
                return callback
            return decorator

        if not callback in self.__events__[event]['callbacks']:
            self.__events__[event]['callbacks'].append(callback)

    def register_event(self, event, triggerman=None):
        """Registers an event with the event dict"""
        self.__events__[event] = {
                "callbacks": [],
                "triggerman": triggerman
                }

    def trigger(self, event, *payload):
        """Runs the event call stack"""
        self._validate_event(event)
        for callback in self.__events__[event]['callbacks']:
            try:
                    callback(*payload)
            except self.ModifyPayload as e:
                payload = e.payload
        return payload

    def triggerman(self, pre_exec=True, post_exec=True):
        """
        Decorator that triggers pre-execution and post-executon events for
        decorated function. Auto-generates event names if none are passed.

        This is kinda nutty. Like, I allow for preempting execution by raising
        an error? WHY?! This allows for some insane shenanigans, and none of
        the code in here should ever be used in production, or in any other
        project. Just don't ok?

        But use FrostyMug, it's fun.
        """
        def decorator(function):
            funcpath = ".".join(function.__qualname__.split(".")[-2:])
            if pre_exec == True:
                pre_exec_name = ".".join((funcpath, "pre-exec"))
            elif isinstance(pre_exec, str):
                pre_exec_name = pre_exec

            if post_exec == True:
                post_exec_name = ".".join((funcpath, "post-exec"))
            elif isinstance(pre_exec, str):
                post_exec_name = post_exec

            if pre_exec:
                self.register_event(pre_exec_name, function)
            if post_exec:
                self.register_event(post_exec_name, function)

            def decorated(*args, **kwargs):
                stop_exec = False
                trigger_post = True
                if pre_exec:
                    try:
                        args, kwargs = self.trigger(pre_exec_name, args, kwargs)
                    except self.StopExecution as e:
                        result = e.result
                        stop_exec = True
                        trigger_post = e.trigger_post

                # I'm literally checking whether we got an exception in that
                # if statement, so if we did I can check other bits... wtf?
                # This is why I love Python. I can do all sorts of really,
                # really terrible things with it.
                if not stop_exec:
                    result = function(*args, **kwargs)
                else:
                    if not trigger_post:
                        return result

                if post_exec:
                    args, kwargs, result = self.trigger(post_exec_name, args, kwargs, result)
                return result
            return decorated
        return decorator
