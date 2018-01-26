class CallbackBase(object):

    def __init__(self, sounds):
        """Init the class.

        :param sounds: The sounds dict with users sound assets.
        :type sounds: dict
        """
        self.sounds = sounds
        self.in_progress = {}

    def _call(self, func, pkt):
        """Run or keep track of running calbacks.

        All callbacks are generators. This function will prime them, run them,
        and keep them running if they are not exhausted and needed to be called again.

        :param func: The function to be called.
        :type func: function
        :param pkt: The packet to feed the supplied function.
        :type pkt: pyshark.packet.Packet
        """
        func_name = str(func)
        cb = self.in_progress.get(func_name)
        if cb:
            try:
                cb.send(pkt)
            except StopIteration:
                    self._prime_generator(func_name, func, pkt)
        else:
            self._prime_generator(func_name, func, pkt)


    def _prime_generator(self, func_name, func, pkt):
        """Make a generator start iterating and store the generator.

        :param func_name: The name of the passed in function.
        :type func_name: string
        :param func: The generator function to be primed.
        :type func: function
        :param pkt: The packet to feed the supplied function.
        :type pkt: pyshark.packet.Packet
        """
        gen = func(pkt)
        next(gen)
        self.in_progress[func_name] = gen
