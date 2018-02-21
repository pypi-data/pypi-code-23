from time import time
import _thread, threading


class APolling(object):
    """Additional base class for driver that need to poll in regular intervals.

    Expects 'poll-interval' in the device yaml configuration.
    """

    _poll_interval = -1  # poll time in seconds
    _stop_loop = None  # threading.Event to signal the poll loop to stop immediately.
    _loop_thread = None  # thread in which the poll loop is executed.
    _verbose_apolling = False  # print debugging information if set to yes.

    def __init__(self, config, verbose):
        self._verbose_apolling = verbose
        self._poll_interval = config["poll-interval"]
        self._stop_loop = threading.Event()

    def _poll_loop(self):
        """Executes _poll_device and then waits (_poll_interval - execution time of _poll_device). This guarantees that
        e.g. the state of a pin is checked exactly each 30 seconds."""
        if self._verbose_apolling:
            print("entered poll_loop method.")

        while not self._stop_loop.isSet():
            start = time()
            self._poll_device()
            sleep_for = max(0, self._poll_interval - (time() - start))

            if self._verbose_apolling:
                print("sleep for " + str(sleep_for) + " seconds.")
            self._stop_loop.wait(sleep_for)

        if self._verbose_apolling:
            print("exiting poll_loop method.")

    # @abstract
    def _poll_device(self):
        """This method must be implemented by the silbing class. Whatever should must be done to poll the device should
        be placed here."""
        raise NotImplementedError("Please implement this method!")

    def _start_polling(self):
        """Start a new thread with _pool_loop. Usually called in the _start_sequence method of the silbling."""
        if self._verbose_apolling:
            print("start loop thread.")
        self._stop_loop.clear()
        self._loop_thread = _thread.start_new_thread(self._poll_loop, ())

    def _stop_polling(self):
        """Stop _pool_loop with Event _stop_loop. Usually called in the _stop_sequence method of the silbling."""
        if self._verbose_apolling:
            print("stopped polling.")
        self._stop_loop.set()

