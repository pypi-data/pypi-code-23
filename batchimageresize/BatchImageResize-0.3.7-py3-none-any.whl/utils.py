from threading import Thread
from multiprocessing import cpu_count


def start_thread(target, name=None, *args):
    """Launch thread."""
    t = Thread(target=target, args=args)
    if name:
        t.name = name
    t.daemon = True
    t.start()
    return t


def start_threads(target, *args):
    """Launch thread in every CPU."""
    threads = []
    for cpu in range(cpu_count()):
        t = start_thread(target, args)
        threads.append(t)
    return threads