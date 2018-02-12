import sys
import inspect
import datetime
from tqdm import trange
from time import sleep

from keyup.colors import Colors
from keyup import logd
from keyup._version import __version__

logger = logd.getLogger(__version__)


def progress_bar(seconds, msg=None, quiet=False):
    """
    Summary:
        Delay timer function with graphical progress bar
        Prints animation to the cli until background process complete
    Args:
        seconds (int): number of timer seconds; delay
        msg (str): progress bar timeout (secs) description caption.

    .. code-block:: python

        # Example:

            msg = 'Process ready in: '
            description.caption = msg + 'X seconds'

    Returns:
        TYPE: bool, Delay Duration End (True) | Delay Duration Interrupt (False)
    """
    seconds = int(seconds)
    logger.info(
        '%s: Received a value of %d seconds for progress delay' % (inspect.stack()[0][3], seconds)
        )

    # eval prerun conditions
    if msg is None:
        msg = '  Process Complete in: '
    if quiet:
        logger.info(
            'quiet is enabled, suppress stdout graphics. Sleeping for %s seconds' %
            int(seconds))
        sleep(seconds)
        return True

    # init
    start = datetime.datetime.utcnow()
    t = trange(100)
    try:
        for i in t:
            # Description will be displayed on the left
            pct_divisor = 100 / seconds
            time_left = (100 - i) / pct_divisor
            t.set_description(
                msg + '%s secs | Progress' %
                (Colors.BOLD + str(round(time_left)) + Colors.RESET)
                )
            # Postfix will be displayed on the right, and will format automatically
            #t.set_postfix(str='h', lst=[1, 2])
            t.set_postfix()
            sleep(seconds / 100)
            dt = datetime.datetime.utcnow() - start
            if time_left == 0 or dt.seconds >= seconds:
                break
        print('\n')
    except Exception as e:
        print(
            '%s: Unknown exception (%s) during progress bar execution.' %
            (inspect.stack()[0][3], str(e))
            )
        raise e
    return True


if __name__ == '__main__':
    delay = input('Enter the number of seconds for progress bar delay function: [20]')
    if not delay:
        delay = 10
    print('delay seconds will be: %d' % int(delay))
    progress_bar(int(delay))
    sys.exit(0)
