import numpy as np
import biosppy.signals.tools as st


class AudioFilter:

    def butter_filter(self, signal, cutoff_frequency, framerate):
        """
        :param signal: .wav data
        :return: butter filtered data
        """

        if (cutoff_frequency == "" or cutoff_frequency == "0"):
            cutoff_frequency = 1000

        cutoff_frequency = int(cutoff_frequency)

        b, a = st.get_filter(ftype="butter",
                             order=2,
                             band="lowpass",
                             frequency=cutoff_frequency,
                             sampling_rate=framerate)

        filtered, zf = st._filter_signal(b, a, signal, check_phase=True)

        max_value = max(filtered)
        filtered = [i / max_value for i in filtered]

        return np.array(filtered)

    def high_pass_filter(self, signal, cutoff_frequency, framerate):
        """
        :param data: imported data -> self.podatki
        :return: filtered .wav data as np array
        """

        if cutoff_frequency == "" or cutoff_frequency == "0":
            cutoff_frequency = 1000

        cutoff_frequency = int(cutoff_frequency)

        filtered, _, _ = st.filter_signal(signal=signal,
                                          ftype='FIR',
                                          band='highpass',
                                          frequency=cutoff_frequency,
                                          order=int(0.3 * 4000),
                                          sampling_rate=framerate)

        return np.array(filtered)

    def low_pass_filter(self, signal, cutoff_frequency, framerate):
        """
        :param data: imported data -> self.podatki
        :return: filtered .wav data as np array
        """

        if cutoff_frequency == "" or cutoff_frequency == "0":
            cutoff_frequency = 1000

        cutoff_frequency = int(cutoff_frequency)

        filtered, _, _ = st.filter_signal(signal=signal,
                                          ftype='FIR',
                                          band='lowpass',
                                          frequency=cutoff_frequency,
                                          order=int(0.3 * 4000),
                                          sampling_rate=framerate)

        return np.array(filtered)
