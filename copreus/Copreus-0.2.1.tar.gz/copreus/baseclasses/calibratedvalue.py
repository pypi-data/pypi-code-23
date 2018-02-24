class CalibratedValue(object):
    """Utility class that takes a value returns a calibrated value.

    Two calibration methods are implemented:
      0. the list calibration_data is empty - the value is returned unchanged.
      1. the list contains exactly one pair - the value is applied with the resulting offset.
      2. the list contains several pairs - the two neighboring (left and right) pairs are selected and the value
      accordingly changed and returned. (this needs an ordered list)

    Additionally a conversion factor can be provided. For example, when using an 12bit DAC for a voltage range of 0-24V
    the conversion factor is 2**12 steps / 24 V = 170.6 steps/V.

    There are two public methods:
      * value(raw) - use it to calibrate measurements. E.g. ADC
      * raw(value) - use it to convert a set point to the value for the device. E.g. DAC
    """
    _calibration_data = None  # ordered list of tuples [[ref_value, raw_value], ...]
    _conversion_factor = -1  # conversion factor
    _method = 0  # internal flag [0,1,2] - is set in __init__ and stores which calibration method should be used
    _offset_value = -1  # internal variable - stores pre-calculated offset for method 1

    _col_ref = 0  # position of reference value in tuple
    _col_raw = 1  # position of raw value in tuple

    def __init__(self, calibration_data, conversion_factor=1):
        self._conversion_factor = conversion_factor
        self._calibration_data = calibration_data # [[ref_value, raw_value], ...]

        if calibration_data is None or len(calibration_data) <= 0:
            self._method = 0
        elif len(calibration_data) == 1:
            self._method = 1
            self._offset_value = self._calibration_data[0][self._col_raw] - self._calibration_data[0][self._col_ref]
        else:
            self._method = 2

    def _corrected(self, value, flip=False):
        """Returns the corrected value. Invokes the correction method according to _method.

        flip is used to change correction direction:
          * False: raw->value
          * True: value->raw"""
        if self._method == 0:
            value = self._no_calib(value)
        elif self._method == 1:
            value = self._offset(value, flip)
        elif self._method == 2:
            value = self._two_points(value, flip)
        else:
            raise ValueError("don't know what to do with method id = {}.".format(self._method))
        return value

    def _no_calib(self, value):
        """returns the unchanged value"""
        return value

    def _offset(self, value, flip):
        """Add/substract _offset_value"""
        if flip:
            value -= self._offset_value
        else:
            value += self._offset_value
        return value

    def _two_points(self, value, flip):
        """Select the surrounding calibration data points and interpolate the calibration value."""
        if flip:
            cref = self._col_raw
            craw = self._col_ref
        else:
            craw = self._col_raw
            cref = self._col_ref

        pos = 1
        while pos < len(self._calibration_data)-1:
            if value <= self._calibration_data[pos][craw]:
                break
            pos = pos + 1

        reflow = self._calibration_data[pos - 1][cref]
        rawlow = self._calibration_data[pos - 1][craw]
        refhigh = self._calibration_data[pos][cref]
        rawhigh = self._calibration_data[pos][craw]

        refrange = refhigh - reflow
        rawrange = rawhigh - rawlow
        corrected = (((value - rawlow) * refrange) / rawrange) + reflow
        return corrected

    def value(self, raw, use_calibration=True):
        """Convert raw measurements into calibrated values. If use_calibration is set to False the unchanged raw value
        is returned (for calibration/testing)."""
        value = raw * self._conversion_factor
        if use_calibration:
            value = self._corrected(value, False)
        return value

    def raw(self, value, use_calibration=True):
        """Convert raw measurements into calibrated values. If use_calibration is set to False the unchanged raw value
        is returned (for calibration/testing)."""
        if use_calibration:
            value = self._corrected(value, True)
        raw = value / self._conversion_factor
        return int(raw)
