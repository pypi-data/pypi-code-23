import subprocess
from subprocess import Popen
from queue import Queue, Empty
from threading import Event, Thread
from typing import Callable, Sequence, IO

from mhelper.exception_helper import SubprocessError


DOnOutput = Callable[[str], None]


def __enqueue_stream( out: IO, queue: Queue, event ) -> None:
    for line in out:
        line = line.decode()
        if line.endswith( "\n" ):
            line = line[:-1]
        queue.put( line )
        event.set()
    
    out.close()


def __wait_exit( process: subprocess.Popen, event: Event ) -> None:
    process.wait()
    event.set()


def async_run( cmds: Sequence[str], on_stdout: DOnOutput, on_stderr: DOnOutput, check: bool = False ) -> int:
    """
    Runs a process asynchronously.
    This function blocks until the process completes, but output is diverted to the provided functions.
    
    Lines received from the standard streams are sent to `on_stdout` and `on_stderr`.
    Any trailing \n are removed.
    Threading is handled, hence these functions are called in the same thread as the one that calls `async_run`. 
     
    :param cmds:                Command sequence to run. See `Popen`.
    :param on_stdout:           Lines received from standard output are sent here. 
    :param on_stderr:           Lines received from standard error are sent here.
    :param check:               When True, a non-zero error code raises an Exception.
    :return:                    The return code of the program.
    :except SubprocessError:    Non-zero error code and `check` was passed as true.
    """
    process = Popen( cmds, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE )
    process.stdin.close()
    
    stdout_queue = Queue()
    stderr_queue = Queue()
    event = Event()
    
    thread_1 = Thread( target = __enqueue_stream, args = (process.stdout, stdout_queue, event) )
    thread_1.name = "async_run.stdout_thread(" + " ".join( cmds ) + ")"
    thread_1.daemon = True
    thread_1.start()
    
    thread_2 = Thread( target = __enqueue_stream, args = (process.stderr, stderr_queue, event) )
    thread_2.name = "async_run.stderr_thread(" + " ".join( cmds ) + ")"
    thread_2.daemon = True
    thread_2.start()
    
    thread_3 = Thread( target = __wait_exit, args = (process, event) )
    thread_2.name = "async_run.exit_thread(" + " ".join( cmds ) + ")"
    thread_3.daemon = True
    thread_3.start()
    
    while True:
        event.wait()
        event.clear()
        
        while True:
            used = False
            
            try:
                line = stdout_queue.get_nowait()
            except Empty:
                pass
            else:
                on_stdout( line )
                used = True
            
            try:
                line = stderr_queue.get_nowait()
            except Empty:
                pass
            else:
                on_stderr( line )
                used = True
            
            if not used:
                break
        
        if process.returncode is not None:
            if check and process.returncode:
                raise SubprocessError( "The command «{}» exited with error code «{}». If available, checking the output may provide more details.".format( " ".join( '"{}"'.format( x ) for x in cmds ), process.returncode ) )
            
            return process.returncode
