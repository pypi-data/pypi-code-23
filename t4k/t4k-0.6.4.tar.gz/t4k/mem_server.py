# saved as greeting-server.py
import setproctitle
import sys
import os
import subprocess
import Pyro4
import multiprocessing

Pyro4.config.SERIALIZERS_ACCEPTED = ('pickle',)
Pyro4.config.SERIALIZER = 'pickle'

@Pyro4.expose
class Provider(object):
    def __init__(self, obj_to_provide):
        self.obj_to_provide = obj_to_provide

    def provide(self):
        return self.obj_to_provide


def mem_get(name):
    return Pyro4.Proxy('PYRONAME:%s' % name).provide()


def remember(name, build_function):

    # First, try to get the object from a memory server
    try:
        print 'trying to remember'
        obj = mem_get(name)
        print 'remembered'

    # If that failed, create the object. Put in a memory server for next time
    except (Pyro4.errors.NamingError, Pyro4.errors.CommunicationError):

        # Make the object
        print 'could not remember... creating'
        obj = build_function()

        # Set the process title for the memory server so that it can be
        # managed using the mem-server command line tool
        setproctitle.setproctitle('memory-server-%s' % name)
        def memory_func():
            server = MemoryServer()
            server.provide(name, obj)
            server.start()

        # Start the memory server process as a detached process
        spawn_daemon(memory_func)


    # Return the object
    return obj


def set_proc_name(newname):
    """
    Modify the title of the process displayed when using the ps command.
    This makes it possible to manage memory server processes using the 
    mem-server command line tool, which finds memory server processes based
    on their name
    """
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)


def spawn_daemon(func):
    """
    Start a process that is detached from the parent, and which continues
    after the parent exists.  That process executes the function ``func``,
    which must take no arguments.
    """
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try: 
        pid = os.fork() 
        if pid > 0:
            # parent process, return and keep running
            return
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

    os.setsid()

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

    # do stuff
    func()

    # all done
    os._exit(os.EX_OK)


class MemoryServer(object):
    """
    The MemoryServer class can be used to make python objects available to 
    other processes.  First, instantiate a MemoryServer object, then call
    memory_server.provide(name, obj), giving a name by which clients will find
    the object, followed by the object itself.  After calling provide for any 
    number of objects, call memory_server.start() to make those objects 
    available.

    clients should use mem_get(name) function in this module to retrieve the
    objects, providing the same name given to the MemoryServer instance.
    """

    def __init__(self):
        self.daemon = Pyro4.Daemon() 
        self.name_server = None


    def provide(self, name, obj):
        """
        Exposes the object ``obj`` which can be retrieved using ``name``
        """
        provider = Provider(obj)
        uri = self.daemon.register(provider)
        self._get_name_server().register(name, uri)


    def _get_name_server(self):
        """
        Returns a name server.  If necessary it starts one up.
        """
        # If we already know the name server, return it
        if self.name_server is not None:
            return self.name_server

        # Otherwise, try to find an existing name server
        try:
            self.name_server = Pyro4.locateNS()

        # If there's no existing name server, then start one
        except Pyro4.errors.NamingError:
            self._start_name_server()
            self.name_server = Pyro4.locateNS()

        # Return the name server.
        return self.name_server


    def _start_name_server(self):
        subprocess.Popen(
            ['pyro4-ns', '-n', '0.0.0.0'],
            env=dict(os.environ, PYRO_SERIALIZERS_ACCEPTED='pickle'),
            stdout=open(os.devnull, 'w'),
            close_fds=True
        )


    def start(self):
        self.daemon.requestLoop()



