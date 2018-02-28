""" Code to read Raymetrics version of Licel binary files."""
import logging

from .licel import LicelFile, LicelLidarMeasurement, LicelChannel, PhotodiodeChannel

logger = logging.getLogger(__name__)


class ScanningFile(LicelFile):
    """ Raymetrics is using a custom version of licel file format to store scanning lidar measurements.
     
    The file includes one extra line describing the scan strategy of the dataset. The extra parameters are:
    
    `azimuth_start`
        Start azimuth angle for the scan, relative to instrument zero position (degrees).
    
    `azimuth_stop`
        Stop azimuth angle for the scan, relative to instrument zero position (degrees).
        
    `azimuth_step` 
        Step of the azimuth scan (degrees).

    `zenith_start` 
        Start zenith angle for the scan, relative to *nadir* (degrees). Take care that this is actually
        nadir angle. Vertical measurements correspond to -90.

    `zenith_stop` 
        Stop zenith angle for the scan, relative to *nadir* (degrees). Take care that this is actually
        nadir angle. Vertical measurements correspond to -90.

    `zenith_step` 
        Step of the zenith scan (degrees).

    `azimuth_offset`
        Offset of instrument zero from North (degrees). Using this value you can convert `azimuth_start` and
        `azimuth_stop` to absolute values.

    Moreover, four new parameters are added in the second line of the file:

    `zenith_angle`
        Zenith angle of the current file. Take care that this is actually
        nadir angle. Vertical measurements correspond to -90.

    `azimuth_angle`
        Azimuth angle of the current file. Value relative to instrument zero position.

    `temperature`
        Ambient temperature (degrees C)

    `pressure`
        Ambient pressure (hPa)
    """

    # Specifications of the header lines.
    licel_file_header_format = ['filename',
                                'start_date start_time end_date end_time altitude longitude latitude zenith_angle azimuth_angle temperature pressure',
                                # Appart from Site that is read manually
                                'azimuth_start azimuth_stop azimuth_step zenith_start zenith_stop zenith_step azimuth_offset',
                                'LS1 rate_1 LS2 rate_2 number_of_datasets', ]

    # Specifications of the channel lines in the header
    licel_file_channel_format = 'active analog_photon laser_used number_of_datapoints 1 HV bin_width wavelength d1 d2 d3 d4 ADCbits number_of_shots discriminator ID'

    def _read_rest_of_header(self, f):
        """ Read the third and fourth row of  of the header lines.

        The first two rows are read in the licel class.

        Parameters
        ----------
        f : file
           An open file-like object.

        Returns
        -------
        raw_info : dict
           A dictionary containing all parameters of the third and fourth line of the header.
        """
        raw_info = {}

        third_line = f.readline()
        raw_info.update(self.match_lines(third_line, self.licel_file_header_format[2]))

        fourth_line = f.readline()
        raw_info.update(self.match_lines(fourth_line, self.licel_file_header_format[3]))
        return raw_info

    def _assign_properties(self):
        """ Assign scanning-specific parameters found in the header as object properties."""
        super(ScanningFile, self)._assign_properties()
        self.azimuth_angle = float(self.raw_info['altitude'])
        self.temperature = float(self.raw_info['temperature'])
        self.pressure = float(self.raw_info['pressure'])
        self.azimuth_start = float(self.raw_info['azimuth_start'])
        self.azimuth_stop = float(self.raw_info['azimuth_stop'])
        self.azimuth_step = float(self.raw_info['azimuth_step'])
        self.zenith_start = float(self.raw_info['zenith_start'])
        self.zenith_stop = float(self.raw_info['zenith_stop'])
        self.zenith_step = float(self.raw_info['zenith_step'])
        self.azimuth_offset = float(self.raw_info['azimuth_offset'])


class ScanningChannel(LicelChannel):
    """ A class representing measurements of a specific lidar channel, during a scanning measurement. """

    def __init__(self):
        super(ScanningChannel, self).__init__()

        self.azimuth_start = None
        self.azimuth_stop = None
        self.azimuth_step = None
        self.zenith_start = None
        self.zenith_stop = None
        self.zenith_step = None
        self.azimuth_offset = None
        self.zenith_angles = []
        self.azimuth_angles = []

    def append_file(self, current_file, file_channel):
        """ Keep track of scanning-specific variable properties of each file. """
        super(ScanningChannel, self).append_file(current_file, file_channel)
        self.zenith_angles.append(current_file.zenith_angle)
        self.azimuth_angles.append(current_file.azimuth_angle)

    def _assign_properties(self, current_file, file_channel):
        """ Assign scanning-specific properties as object properties. Check that these are unique,
        i.e. that all files belong to the same measurements set.

        Parameters
        ----------
        current_file : ScanningFile object
           A ScanningFile object being imported
        file_channel : LicelChannelData object
           A specific LicelChannelData object holding data found in the file.
        """
        super(ScanningChannel, self)._assign_properties(current_file, file_channel)
        self._assign_unique_property('azimuth_start', current_file.azimuth_start)
        self._assign_unique_property('azimuth_stop', current_file.azimuth_stop)
        self._assign_unique_property('azimuth_step', current_file.azimuth_step)
        self._assign_unique_property('zenith_start', current_file.zenith_start)
        self._assign_unique_property('zenith_stop', current_file.zenith_stop)
        self._assign_unique_property('zenith_step', current_file.zenith_step)


class ScanningLidarMeasurement(LicelLidarMeasurement):
    """ A class representing a scanning measurement set.

    It useses `ScanningFile` and `ScanningChannel` classes for handling the data.
    """
    file_class = ScanningFile
    channel_class = ScanningChannel
    photodiode_class = PhotodiodeChannel
