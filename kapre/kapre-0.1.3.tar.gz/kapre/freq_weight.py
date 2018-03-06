class FrequencyWeighting(Layer):
    """

    The computation code is from librosa.
    Brian, thanks x NaN!

    """

    def __init__(self, mode, frequencies, decibel, power, **kwargs):
        """
        mode: 'A' 'a' for A-weighting
        frequencies: list of float or 1d np array, center frequencies.
        decibel: Bool, true if input is decibel scale (log(X))
        power: float but probably either 1.0 or 2.0.
        E.g., if input is power spectrogram which is log(X**2),
            power = 2.0,
            decibel = True
        If decibel:
            in call(), weights are ADDED.
        else:
            in call(), weights are MULTIPLIED.

        """
        # TODO: Current code is for keras v1.
        assert mode.lower() in ('a')
        self.mode = mode
        self.frequencies = frequencies
        self.decibel = decibel
        self.power = power
        super(FrequencyWeighting, self).__init__(**kwargs)

        freq_weights = backend.a_weighting(self.frequencies)

        if power != 2.0:
            freq_weights *= (power / 2.0)
        if decibel:
            self.freq_weights = K.variable(freq_weights, dtype=K.floatx())
        else:
            self.freq_weights = K.variable(10. ** freq_weights, dtype=K.floatx())

    def call(self, x, mask=None):
        if self.decibel:
            return x + self.freq_weights
        else:
            return x * self.freq_weights

    def get_config(self):
        config = {'mode': self.mode,
                  'frequencies': self.frequencies,
                  'decibel': self.decibel}
        base_config = super(FrequencyWeighting, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
