import os, signal


def killme_after(delay, loop, sig='SIGINT', pid=None):
    """
    :param delay: delay in seconds to execute signal
    :param loop: asyncio event loop
    :param sig: signal (string), must presents in signal package
    :param pid: PID (default is current PID)
    :return:
    """
    if not hasattr(signal, sig):
        print('unknown signal "%s"' % sig)
    else:
        if not getattr(loop, 'sig_%s' % sig, False):
            loop.call_later(delay, os.kill, pid or os.getpid(), getattr(signal, sig))
            setattr(loop, 'sig_%s' % sig, True)
