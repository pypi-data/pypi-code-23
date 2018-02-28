""" This is a class for experimenting with the new DIVA / EARLINET NetCDF file format.

In the long run, this should be places as a method in BaseLidarMeasurement class. For now it is kept
separately not to interfere with normal development.
"""
import netCDF4 as netcdf
import yaml
import datetime
import os
import numpy as np

import pytz

from .generic import BaseLidarMeasurement


class DivaOutput(BaseLidarMeasurement):

    def save_as_diva_netcdf(self, output_path, parameter_file):
        """ Save the current data in the 'draft' DIVA format. """

        with open(parameter_file, 'r') as f:
            parameters = yaml.load(f)

        global_parameters = parameters['global_parameters']  # Shortcut
        global_variables = parameters['global_variables']  # Shortcut
        channels = parameters['channels']


        iso_date = datetime.datetime.utcnow().isoformat()
        python_file_name = os.path.basename(__file__)

        with netcdf.Dataset(output_path, 'w', format="NETCDF4") as f:

            # Global attributes
            f.title = global_parameters['title']
            f.source = global_parameters['source']
            f.institution = global_parameters['institution']
            f.references = global_parameters['references']
            f.location = global_parameters['location']
            f.data_version = global_parameters['data_version']
            f.PI = global_parameters['PI_name']
            f.PI_email = global_parameters['PI_email']
            f.conversion_date = iso_date
            f.comment = global_parameters['comment']
            f.Conventions = global_parameters['Conventions']
            f.history = global_parameters['history'].format(date=iso_date, file=python_file_name)
            f.featureType = "timeSeriesProfile"

            # Top level dimensions
            f.createDimension('name_strlen', size=40)
            f.createDimension('nv', size=2)

            # Top level variables
            latitude = f.createVariable('latitude', datatype='f4')
            latitude.standard_name = 'latitude'
            latitude.long_name = 'system latitude'
            latitude.units = 'degrees_north'

            longitude = f.createVariable('longitude', datatype='f4')
            longitude.standard_name = 'longitude'
            longitude.long_name = 'system longitude'
            longitude.units = 'degrees_east'

            laser_angle = f.createVariable('laser_zenith_angle', datatype='f4')
            laser_angle.standard_name = 'sensor_zenith_angle'
            laser_angle.long_name = 'zenith angle of emitted laser'
            laser_angle.units = 'degree'

            laser_azimuth = f.createVariable('laser_azimuth_angle', datatype='f4')
            laser_azimuth.standard_name = 'sensor_azimuth_angle'
            laser_azimuth.long_name = 'azimuth angle of emitted laser'
            laser_azimuth.units = 'degree'
            laser_azimuth.comment = 'Based on North. Optional'

            altitude = f.createVariable('altitude', datatype='f4')
            altitude.standard_name = 'altitude'
            altitude.long_name = 'system altitude'
            altitude.units = 'm'

            # Assign top-level variables
            latitude[:] = global_variables['latitude']
            longitude[:] = global_variables['longitude']
            laser_angle[:] = global_variables['laser_pointing_angle']
            altitude[:] = global_variables['system_altitude']

            # Optional ancillary group
            ancillary = f.createGroup('ancillary')
            ancillary.featureType = "timeSeries"

            ancillary.createDimension('time', size=None)

            time = ancillary.createVariable('time', datatype='f8', dimensions=('time',))
            time.long_name = 'time'
            time.units = 'seconds since 1970-01-01 00:00'
            time.standard_name = 'time'

            temperature = ancillary.createVariable('air_temperature', datatype='f8', dimensions=('time',))
            temperature.long_name = 'air temperature at instrument level'
            temperature.units = 'K'
            temperature.standard_name = 'air_temperature'

            pressure = ancillary.createVariable('air_pressure', datatype='f8', dimensions=('time',))
            pressure.long_name = 'air pressure at instrument level'
            pressure.units = 'hPa'
            pressure.standard_name = 'air_pressure'

            # Create a separate group for each channel
            for channel_name, channel_parameters in channels.iteritems():

                if channel_name not in self.channels.keys():
                    raise ValueError('Channel name not one of {0}: {1}'.format(self.channels.keys(), channel_name))

                channel = self.channels[channel_name]

                group_name = "channel_{0}".format(channel_name.replace('.', '_'))  # Give channels groups a standard name

                g = f.createGroup(group_name)
                g.long_name = channel_parameters['long_name']
                g.detector_manufacturer = channel_parameters['detector_manufacturer']    # Optional
                g.detector_model = channel_parameters['detector_model']
                g.daq_manufacturer = channel_parameters['daq_manufacturer']
                g.daq_model = channel_parameters['daq_model']

                # Dimensions
                g.createDimension('profile', size=None)  # Infinite dimension
                g.createDimension('range', len(channel.z))

                # Variables
                name = g.createVariable('channel_id', 'c', dimensions=('name_strlen',))
                name.cf_role = 'timeseries_id'
                name.long_name = 'channel identification'

                laser_rep_rate = g.createVariable('laser_repetition_rate', 'f4')
                laser_rep_rate.long_name = 'nominal laser repetition rate'
                laser_rep_rate.units = 'Hz'

                # TODO: Emission wavelength ??


                emission_energy = g.createVariable('emission_energy', datatype='f8', )  # or dimensions=('profile',)
                emission_energy.long_name = 'emission energy per pulse'
                emission_energy.units = 'mJ'
                emission_energy.comment = "could be scalar, if value is nominal."

                emission_pol = g.createVariable('emission_polarization', datatype='b')
                emission_pol.long_name = 'nominal emission poalrization'
                emission_pol.flag_values = '0b 1b 2b'
                emission_pol.flag_meanings = 'linear circular none'

                fov = g.createVariable('fov', datatype='f4')
                fov.long_name = 'channel field of view full angle'
                fov.units = 'mrad'
                fov.comment = 'simulated'

                detector_type = g.createVariable('detector_type', datatype='b')
                detector_type.long_name = 'detector type'
                detector_type.flag_values = '0b 1b'
                detector_type.flag_meanings = 'PMT APD'

                detection_mode = g.createVariable('detection_mode', datatype='b')
                detection_mode.long_name = 'detection mode'
                detection_mode.flag_values = '0b 1b'
                detection_mode.flag_meanings = 'analog photon_counting'

                detection_cw = g.createVariable('detection_wavelength', datatype='f8')
                detection_cw.long_name = 'center wavelength of detection filters'
                detection_cw.units = 'nm'
                detection_cw.standard_name = 'sensor_band_central_radiation_wavelength'

                detection_fwhm = g.createVariable('detection_fwhm', datatype='f8')
                detection_fwhm.long_name = 'FWHM of detection filters'
                detection_fwhm.units = 'nm'

                detection_pol = g.createVariable('detection_polarization', datatype='b')
                detection_pol.long_name = 'nominal detection poalrization'
                detection_pol.flag_values = '0b 1b 2b'
                detection_pol.flag_meanings = 'linear circular total'

                polarizer_angle = g.createVariable('polarizer_angle', datatype='f4', dimensions=('profile', ), zlib=True)
                polarizer_angle.long_name = 'polarizer angle in respect to laser plane of polarization'
                polarizer_angle.units = 'degree'
                polarizer_angle.comments = 'Optional'

                if not channel.is_analog:
                    dead_time_model = g.createVariable('dead_time_model', datatype='b')
                    dead_time_model.long_name = 'optimal dead time model of detection system'
                    dead_time_model.flag_values = '0b 1b 2b'
                    dead_time_model.flag_meanings = 'paralyzable non_paralyzable other'

                    dead_time = g.createVariable('dead_time', datatype='f8')
                    dead_time.long_name = 'dead time value'
                    dead_time.units = 'ns'
                    dead_time.comment = "Manufacturer. Source of the value."

                bin_length = g.createVariable('bin_length', datatype='f4')
                bin_length.long_name = "time duration of each bin"
                bin_length.units = 'ns'

                if channel.is_analog:
                    adc_bits = g.createVariable('adc_bits', datatype='i4')
                    adc_bits.long_name = 'analog-to-digital converter bits'
                    adc_bits.coordinates = "time"

                detector_voltage = g.createVariable('detector_voltage', datatype='f4', dimensions=('profile',), zlib=True)
                detector_voltage.long_name = 'detector voltage'
                detector_voltage.units = 'V'
                detector_voltage.coordinates = "time"

                if channel.is_photon_counting:
                    discriminator = g.createVariable('discriminator', datatype='f8', dimensions=('profile',))
                    discriminator.long_name = 'discriminator level'
                    discriminator.units = ''

                if channel.is_analog:
                    adc_range = g.createVariable('adc_range', datatype='f4', dimensions=('profile',),
                                                        zlib=True)
                    adc_range.long_name = 'analog-to-digital converter range'
                    adc_range.units = 'mV'
                    adc_range.coordinates = "time"

                pulses = g.createVariable('pulses', datatype='i4', dimensions=('profile',),
                                          zlib=True)
                pulses.long_name = 'accumulated laser pulses per record'
                pulses.coordinates = "time"

                nd_filter = g.createVariable('nd_filter_od', datatype='f8', dimensions=('profile',))
                nd_filter.long_name = "neutral density filter optical depth "
                nd_filter.coordinates = "time"

                trigger_delay = g.createVariable('trigger_delay', datatype='f4')
                trigger_delay.long_name = "channel trigger difference from pulse emission"
                trigger_delay.units = 'ns'
                trigger_delay.comments = 'Negative values for pre-trigger systems.'

                time = g.createVariable('time', datatype='f8', dimensions=('profile',),
                                        zlib=True)
                time.long_name = 'profile start time '
                time.units = "seconds since 1970-01-01 00:00:00"
                time.standard_name = "time"
                time.bounds = "time_bnds"
                time_bounds = g.createVariable('time_bnds', datatype='f8', dimensions=('profile', 'nv'), zlib=True)

                bin_time = g.createVariable('bin_time', datatype='f4', dimensions=('range',), zlib=True)
                bin_time.long_name = 'bin start time since channel trigger'
                bin_time.units = "ns"

                if channel.is_analog:
                    signal_units = 'mV'
                    signal_datatype = 'f8'
                else:
                    signal_units = 'counts'
                    signal_datatype = 'i8'

                signal = g.createVariable('signal', datatype=signal_datatype, dimensions=('profile', 'range'),
                                          zlib=True)
                signal.long_name = 'signal'
                signal.units = signal_units
                signal.coordinates = "time"
                signal.ancillary_variables = "signal_stddev"

                # If measured
                signal_stddev = g.createVariable('signal_stddev', datatype=signal_datatype, dimensions=('profile', 'range'),
                                          zlib=True)
                signal_stddev.long_name = 'signal standard deviation'
                signal_stddev.units = signal_units
                signal_stddev.coordinates = "time"
                signal_stddev.comments = "Only if measured. Should be removed if not."

                # Assign variables
                name[:len(channel_name)] = channel_name
                laser_rep_rate[:] = channel_parameters['laser_repetition_rate']
                emission_energy[:] = channel_parameters['emission_energy']
                emission_pol[:] = self._emission_pol_flag(channel_parameters['emission_polarization'])
                fov[:] = channel_parameters['fov']
                detector_type[:] = self._detector_type_flag(channel_parameters['detector_type'])
                detection_mode[:] = self._detection_mode_flag(channel_parameters['detection_mode'])
                detection_fwhm[:] = channel_parameters['filter_fwhm']
                detection_pol[:] = self._detection_pol_flag(channel_parameters['detection_polarization'])
                polarizer_angle[:] = channel_parameters['polarizer_angle'] * np.ones(len(channel.time))  # For now, assumed constant.

                if channel.is_photon_counting:
                    dead_time_model[:] = self._deadtime_model_flag(channel_parameters['dead_time_model'])
                    dead_time[:] = channel_parameters['dead_time']

                bin_length[:] = channel_parameters['bin_length']
                trigger_delay[:] = channel_parameters['trigger_delay']

                detector_voltage[:] = channel.hv

                if channel.is_analog:
                    adc_range[:] = channel.discriminator
                    adc_bits[:] = channel.adcbits
                else:
                    discriminator[:] = channel.discriminator

                pulses[:] = channel.laser_shots

                epoch = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)
                seconds_since_epoch = [(t - epoch).total_seconds() for t in channel.time]
                time[:] = seconds_since_epoch
                time_bounds[:, 0] = seconds_since_epoch
                time_bounds[:, 1] = seconds_since_epoch + channel.get_duration()

                bin_time[:] = channel.binwidth * np.arange(len(channel.z))

                signal[:] = channel.matrix

    def _deadtime_model_flag(self, model_str):
        """ Convert dead-time model string to byte flag.

        Parameters
        ----------
        model_str : str
           String describing the dead-time model (one of paralyzable, non-paralyzable, or other)

        Returns
        -------
        : int
           Byte encoding of dead-time model
        """
        choices = {'paralyzable': 0,
                   'non-paralyzable': 1,
                   'other': 2}

        if model_str not in choices.keys():
            raise ValueError('Dead-time model is not one of {0}: {1}'.format(choices.keys(), model_str))

        return choices[model_str]

    def _detection_pol_flag(self, pol_str):
        """ Convert detection  polarization string to byte flag.

        Parameters
        ----------
        pol_str : str
           String describing the detection polarization (one of linear, circular, or total)

        Returns
        -------
        : int
           Byte encoding of detection polarization
        """
        choices = {'linear': 0,
                   'circular': 1,
                   'total': 2}

        if  pol_str not in choices.keys():
            raise ValueError('Detection polarization is not one of {0}: {1}'.format(choices.keys(), pol_str))

        return choices[pol_str]

    def _detection_mode_flag(self, mode_str):
        """ Convert detection  mode string to byte flag.

        Parameters
        ----------
        mode_str : str
           String describing the detector mode (one of photon-counting or analog)

        Returns
        -------
        : int
           Byte encoding of detection mode
        """
        choices = {'analog': 0,
                   'photon-counting': 1,}

        if  mode_str not in choices.keys():
            raise ValueError('Detection mode is not one of {0}: {1}'.format(choices.keys(), mode_str))

        return choices[mode_str]

    def _detector_type_flag(self, type_string):
        """ Convert emission string to byte flag.

        Parameters
        ----------
        type_string : str
           String describing the detector type (one of APD or PMT)

        Returns
        -------
        : int
           Byte encoding of detector type
        """
        choices = {'PMT': 0,
                   'APD': 1,}

        if  type_string not in choices.keys():
            raise ValueError('Detector type is not one of {0}: {1}'.format(choices.keys(), type_string))

        return choices[type_string]

    def _emission_pol_flag(self, pol_string):
        """ Convert emission string to byte flag.

        Parameters
        ----------
        pol_string : str
           String describing the polarization (one of linear, circular, or none)

        Returns
        -------
        : int
           Byte encoding of polarization state
        """
        choices = {'linear': 0,
                   'circular': 1,
                   'none': 2}

        if pol_string not in choices.keys():
            raise ValueError('Emission polarization not one of {0}: {1}'.format(choices.keys(), pol_string))

        return choices[pol_string]
