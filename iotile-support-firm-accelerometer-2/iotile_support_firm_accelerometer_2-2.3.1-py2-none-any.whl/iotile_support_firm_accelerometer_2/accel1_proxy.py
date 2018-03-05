import math
import struct
import logging
import datetime
import uuid
from monotonic import monotonic
from contextlib import contextmanager
from iotile.core.hw.proxy.proxy import TileBusProxyObject
from iotile.core.hw.proxy.plugin import TileBusProxyPlugin
from typedargs.annotate import param, return_type, context, annotated, docannotate
from typedargs import iprint
from iotile.core.exceptions import HardwareError, ArgumentError, ExternalError, DataError
from iotile.core.utilities.console import ProgressBar


@context("AccelProxy")
class AccelProxy(TileBusProxyObject):
    """
    Provide access to Accelerometer tile functionality

    :param stream: CMDStream instance that can communicate with this tile
    :param addr: Local tilebus address of this tile
    """

    SAMPLE_RATES = {
        0: 3200,
        1: 1600,
        2: 800,
        3: 400
    }

    LSB_VALUE = 0.049  # The ADXL375 reports data in 49 mg/LSB

    @classmethod
    def ModuleName(cls):
        return 'accel1'

    def __init__(self, stream, addr):
        super(AccelProxy, self).__init__(stream, addr)

        self._waveform_manager = WaveformManager(self)
        self._setup_manager = SetupManager(self)
        self._calibration_manager = CalibrationManager(self)
        self._test_manager = TestManager(self)

    @annotated
    def calibration_manager(self):
        """Get a CalibrationManager object."""
        return self._calibration_manager

    @annotated
    def setup_manager(self):
        """Get a SetupManager object."""
        return self._setup_manager

    @annotated
    def waveform_manager(self):
        """Get a WaveformManager instance."""

        return self._waveform_manager

    @annotated
    def test_manager(self):
        """Get a TestManager instance."""

        return self._test_manager

    @return_type('integer')
    def count_shocks(self):
        """Count the number of shocks recorded since power on.

        :rtype: 32-bit unsigned integer
        """

        status = self._setup_manager.get_status()
        return status['shock_counter']

    def get_shock(self, name):
        """Get a cached shock, either last, peak_g or max_dv.

        Args:
            name (str): The name of the stored shock that we want to obtains.
                This must be one of last, peak_g, or max_dv

        Returns:
            dict: A dictionary for the last recorded shock event containing the following keys:
                peak_axis (str): X, Y or Z
                length (int): The number of ms the event exceeded the programmed threshold
                peak (float): The peak acceleration experienced on the peak axis of the event in G's
                deltav_x (float): The total change in velocity in the x direction (in m/s)
                deltav_y (float): The total change in velocity in the y direction (in m/s)
                deltav_z (float): The total change in velocity in the z direction (in m/s)
                average_x (float): The average value of the shock in the x direction (in G's)
                average_y (float): The average value of the shock in the y direction (in G's)
                average_z (float): The average value of the shock in the z direction (in G's)
        """

        names = {
            'last': 0,
            'max_g': 1,
            'max_dv': 2
        }

        index = names.get(name)
        if index is None:
            raise ArgumentError("Unknown shock name", name=name, known_names=[x for x in names])

        peak, length, data_x, data_y, data_z = self.rpc(0x80, 0x04, 0, index, arg_format="BB", result_format="HHlll")

        event = {
            'peak_axis': _convert_axis(peak & 0b11),
            'peak': (peak >> 2) * self.LSB_VALUE,
            'length': length,
            'deltav_x': data_x,
            'deltav_y': data_y,
            'deltav_z': data_z
        }

        _convert_event(event)

        return event

    @return_type('basic_dict')
    def last_shock(self):
        """Get the last shock recorded by the device.

        Returns:
            dict: A dictionary for the last recorded shock event containing the following keys:
                peak_axis (str): X, Y or Z
                length (int): The number of ms the event exceeded the programmed threshold
                peak (float): The peak acceleration experienced on the peak axis of the event in G's
                deltav_x (float): The total change in velocity in the x direction (in m/s)
                deltav_y (float): The total change in velocity in the y direction (in m/s)
                deltav_z (float): The total change in velocity in the z direction (in m/s)
                average_x (float): The average value of the shock in the x direction (in G's)
                average_y (float): The average value of the shock in the y direction (in G's)
                average_z (float): The average value of the shock in the z direction (in G's)
        """

        return self.get_shock('last')

    @return_type('basic_dict')
    def peakg_shock(self):
        """Get the shock with the largest peak g recorded by the device.

        Returns:
            dict: A dictionary for the recorded shock event containing the following keys:
                peak_axis (str): X, Y or Z
                length (int): The number of ms the event exceeded the programmed threshold
                peak (float): The peak acceleration experienced on the peak axis of the event in G's
                deltav_x (float): The total change in velocity in the x direction (in m/s)
                deltav_y (float): The total change in velocity in the y direction (in m/s)
                deltav_z (float): The total change in velocity in the z direction (in m/s)
                average_x (float): The average value of the shock in the x direction (in G's)
                average_y (float): The average value of the shock in the y direction (in G's)
                average_z (float): The average value of the shock in the z direction (in G's)
        """

        return self.get_shock('max_g')

    @return_type('basic_dict')
    def maxdv_shock(self):
        """Get the shock with the largest delta-v recorded by the device.

        Returns:
            dict: A dictionary for the recorded shock event containing the following keys:
                peak_axis (str): X, Y or Z
                length (int): The number of ms the event exceeded the programmed threshold
                peak (float): The peak acceleration experienced on the peak axis of the event in G's
                deltav_x (float): The total change in velocity in the x direction (in m/s)
                deltav_y (float): The total change in velocity in the y direction (in m/s)
                deltav_z (float): The total change in velocity in the z direction (in m/s)
                average_x (float): The average value of the shock in the x direction (in G's)
                average_y (float): The average value of the shock in the y direction (in G's)
                average_z (float): The average value of the shock in the z direction (in G's)
        """

        return self.get_shock('max_dv')

    @return_type('list(integer)')
    def last_sample(self):
        """Get the latest raw x, y and z acceleration values."""

        return self._setup_manager.get_status()['last_sample']

    @return_type("integer")
    def last_x(self):
        """Get the last unfiltered x value from the accelerometer."""

        return self.last_sample()[0]

    @return_type("integer")
    def last_y(self):
        """Get the last unfiltered y value from the accelerometer."""

        return self.last_sample()[1]

    @return_type("integer")
    def last_z(self):
        """Get the last unfiltered z value from the accelerometer."""

        return self.last_sample()[2]


@context("WaveformManager")
class WaveformManager(TileBusProxyPlugin):
    """A proxy plugin for managing waveform storage.

    This manager provides access to the flash memory on the accelerometer
    tile including the ability to download readings, clear data and trigger
    an immediate waveform capture.

    Args:
        parent (TileBusProxyObject): The parent of this plugin.
    """

    FLASH_RECORD_MAGIC = 0x44332211
    FLASH_RECORD_VERSION = 3

    STREAMING_HEADER_SIZE = 20

    def __init__(self, parent):
        super(WaveformManager, self).__init__(parent)

        self.logger = logging.getLogger(__name__)

    @annotated
    def capture_waveform(self):
        """Capture a single waveform immediately.

        The waveform is saved to flash in the next available capture location.
        """

        error, = self.rpc(0x80, 0x34, result_format="L")
        if error != 0:
            raise HardwareError("Unable to capture a single waveform", error_code=error)

    @docannotate
    def load_waveform(self, index):
        """Load and compress a waveform from flash into RAM.

        This is the first step of streaming a waveform out of the device.
        It is loaded and compressed into RAM and then streamed at highspeed
        from RAM.

        Args:
            index (int): The index of the waveform that we wish to load.

        Returns:
            basic_dict: A dictionary of information about the
                loaded waveform including its compressed size and compression
                ratio.
        """

        start = monotonic()
        err1, err2, size, loaded_index = self.rpc(0x80, 0x3c, index, arg_format="H", result_format="HHHH")
        if err1 != 0 or err2 != 0:
            raise HardwareError("Error loading compressed waveform", index=index, error_1=err1, error_2=err2)
        end = monotonic()

        result = {
            'initial_size': 6*1024,
            'compressed_size': size,
            'loaded_index': loaded_index,
            'compression_ratio': 100.0 - ((float(size) / (6*1024)) * 100.0),
            'load_time_ms': int((end - start)*1000)
        }

        return result

    def stream_waveform(self, index):
        """Load and stream the currently loaded waveform at highspeed.

        Args:
            index (int): The index of the waveform that we wish to load.

        Returns:
            basic_dict: A dictionary with information about the waveform
        """

        info = self.load_waveform(index)

        self._proxy._hwmanager.enable_tracing()

        err, = self.rpc(0x80, 0x3d, result_format="L")
        if err:
            raise HardwareError("Error trigging compressed waveform streaming", error_code=err)

        start = monotonic()
        data = self._proxy._hwmanager.wait_trace(info['compressed_size'] + self.STREAMING_HEADER_SIZE, timeout=5.0)
        end = monotonic()

        stream_time = int((end - start)*1000)
        wave = self._process_compressed_waveform(data)
        return wave

    def _process_waveform_header(self, compressed_data):
        """Expand and check waveform data received in a compressed format."""

        if len(compressed_data) < self.STREAMING_HEADER_SIZE:
            raise DataError("Corrupted waveform data received that was too short to contain a valid header", length=len(compressed_data))

        header = compressed_data[:self.STREAMING_HEADER_SIZE]

        fmt_code, compressed_size, unique_id, timestamp, crc_code = struct.unpack("<BxHLLL4x", header)

        if fmt_code != 1:
            raise DataError("Unknown streamed waveform format code", fmt_code=fmt_code)

        return {
            'unique_id': unique_id,
            'timestamp': timestamp,
            'crc32_value': crc_code,
            'compressed_length': compressed_size,
        }

    def _verify_crc_code(self, compressed_data, crc_code):
        try:
            import crcmod
            crc32_func = crcmod.mkCrcFun(0x104C11DB7, initCrc=0xFFFFFFFF, rev=False, xorOut=0)

            checksum = crc32_func(bytes(compressed_data)) & 0xFFFFFFFF
            if checksum == crc_code:
                return 'valid'
            
            return 'invalid'
        except ImportError:
            return 'not_performed'

    def _process_compressed_waveform(self, compressed_data, window_size=8, lookahead_size=4):
        """Expand and check waveform data received in a compressed format."""

        header = self._process_waveform_header(compressed_data)
        encoded_waveform = compressed_data[self.STREAMING_HEADER_SIZE:]

        if header['compressed_length'] != len(encoded_waveform):
            raise DataError("Corrupted waveform data that did not match the included waveform length", embedded_length=header['compressed_length'], actual_length=len(encoded_waveform))

        decoder = HeatshrinkDecoder(window_size, lookahead_size)
        decoder.decode(encoded_waveform)

        data = decoder.output

        expanded_data = struct.unpack("%dB" % (len(data),), data)
        unpacked_data = []

        accum = 0
        shift = 0
        for val in expanded_data:
            if val & (1 << 7):
                accum |= (val & 0x7f)
                shift = 7
            else:
                accum |= ((val & 0x7f) << shift)
                zigzag = ((accum >> 1) ^ -(accum & 1))

                unpacked_data.append(zigzag)
                accum = 0
                shift = 0

        for i in xrange(1, len(unpacked_data)):
            unpacked_data[i] += unpacked_data[i - 1]

        if len(unpacked_data) != (3*1024):
            raise DataError("Corrupted waveform that did not contain 1024 3-reading samples", length=len(unpacked_data))

        x_list = [x * self._proxy.LSB_VALUE for x in unpacked_data[:1024]]
        y_list = [x * self._proxy.LSB_VALUE for x in unpacked_data[1024:2048]]
        z_list = [x * self._proxy.LSB_VALUE for x in unpacked_data[2048:]]

        header['data'] = {
            'x': x_list,
            'y': y_list,
            'z': z_list
        }

        header['crc_verification'] = self._verify_crc_code(encoded_waveform, header['crc32_value'])

        return header

    @annotated
    def enter_streaming_mode(self):
        """Prepare the device to stream waveforms."""

        error, = self.rpc(0x80, 0x38, result_format="L")
        if error != 0:
            raise HardwareError("Unable to enter streaming mode", error_code=error)

    @annotated
    def leave_streaming_mode(self):
        """Prepare the device to stream waveforms."""

        error, = self.rpc(0x80, 0x39, result_format="L")
        if error != 0:
            raise HardwareError("Unable to enter streaming mode", error_code=error)

    @docannotate
    def sorted_waveform_list(self):
        """Download the list of the top N waveform indices stored in flash.

        You must have previously called sort_waveforms to sort the waveforms
        and you must be in streaming mode.  Given those two things this
        function will download the indices of the top N waveforms where N
        is the the count given to sort_waveforms.

        Returns:
            list(int): A list of the top N waveform indices.
        """

        offset = 0
        indices = []

        while True:
            res = self.rpc(0x80, 0x3b, offset, arg_format="H", result_type=(0, True))
            buff = res['buffer']

            if len(buff) == 0:
                break

            chunk = struct.unpack("<%dH" % (len(buff) / 2), buff)
            indices += chunk
            offset += len(chunk)

        return indices

    @docannotate
    def stream_sorted_waveforms(self):
        """Stream and decode all waveforms currently sorted in the tile.
        
        This function will synchronously stream and wait for all of the "top"
        waveforms currently sorted in the tile to be streamed at highspeed.

        It decodes each one, verifies its CRC code and returns a list of all
        of them as dictionaries.

        Returns:
            basic_dict: A list of all of the decoded waveforms received from the tile.
        """

        hw = self._proxy._hwmanager
        hw.enable_tracing()

        err, count, _unused = self.rpc(0x80, 0x3e, result_format="HHH")
        if err:
            raise HardwareError("Unknown error starting waveform streaming", error_code=err)

        prog = ProgressBar("Streaming %d Waveforms" % count, count*100)
        prog.start()

        i = 0

        def _progress_updater(finished, total):
            frac = float(finished) / total
            prog.progress(int((i + frac) * 100))

        waveforms = []

        self.logger.info("Preparing to stream %d waveforms", count)

        try:
            for i in xrange(0, count):
                raw_header = hw.wait_trace(self.STREAMING_HEADER_SIZE, 2.0)
                header = self._process_waveform_header(raw_header)
                self.logger.info("Received header for waveform %d of %d, header=%s", i + 1, count, header)
                data = hw.wait_trace(header['compressed_length'], 5.0, progress_callback=_progress_updater)
                self.logger.info("Received %d bytes of compressed waveform data", header['compressed_length'])
                waveform = self._process_compressed_waveform(raw_header + data)
                waveforms.append(waveform)

                prog.progress((i+1) * 100)
        finally:
            prog.end()

        return waveforms

    @docannotate
    def sort_waveforms(self, sort="peak_g", count=100, skip_id=0):
        """Sort all stored waveforms on the tile and keep the largest count.

        This RPC instructs the tile to perform a max-k algorithm on all of the
        stored waveforms in the tile's flash memory and keep the top count events.

        The index of these events is then available for streaming off of the tile
        in highspeed waveform streaming mode.

        Args:
            sort (str): The key to use to sort events, you can specify either
                peak_g or max_dv.
            count (int): The maximum number of events to keep, if you want the
                top 10 events, for example, count should be 10.
            skip_id (int): A unique id from the tile that specifies that all
                events up until and including that one should be ignored.  This
                allows you to perform incremental sorts where you download
                waveforms up to a point and then want to download the largest
                new events after that point.  By default, no events are skipped.

        Returns:
            int: The number of events that were ultimately included in the resulting
                list.  If an error occurs during sort it it thrown as an exception.
        """

        sort_codes = {
            'peak_g': 0,
            'max_dv': 1
        }

        sort_code = sort_codes.get(sort)
        if sort_code is None:
            raise ArgumentError("Unknown sort criteria", criteria=sort, known_criteria=[x for x in sort_codes])

        err, return_count = self.rpc(0x80, 0x3a, skip_id, count, sort_code, arg_format="LHB", result_format="LL")

        if err != 0:
            raise HardwareError("Unable to sort waveforms", error_code=err)

        return return_count

    @docannotate
    def dump_waveform_table(self, out_path):
        """Save the waveform handle table.

        Args:
            out_path (str): The path to save the data to as a binary file.
        """

        data = self.download_flash(0, 4096*2)

        with open(out_path, "wb") as outfile:
            outfile.write(data)

    def download_flash(self, base_address, length, message="Downloading Flash"):
        """Download data from flash.

        Args:
            base_address (int): The address to start downloading from
            length (int): The number of bytes to download
            message (str): The message to show with the downloading progress bar

        Returns:
            bytearray: The raw data downloaded from flash
        """

        acc = bytearray()

        prog = ProgressBar(message, length)

        prog.start()
        for i in xrange(0, length, 20):
            chunk_length = min(20, length - i)
            addr = base_address + i

            res = self.rpc(0x80, 0x32, addr, arg_format="L", result_type=(0, True))
            buff = res['buffer']
            if len(buff) == 0:
                raise HardwareError("Not performing flash download at invalid time that could cause collision with onboard processing")

            buff = buff[:chunk_length]
            acc += buff

            prog.progress(i)

        prog.end()

        return acc

    @param("record", "integer", "nonnegative")
    @return_type("basic_dict")
    def download_metadata(self, record):
        """Download the header metadata for a given waveform record.

        Args:
            record (int): The record number of the saved record to download

        Returns:
            dict: A dictionary of metadata about the waveform.
        """

        download_size = 256
        data = self.download_flash((record+1)*8192, download_size, message="Downloading Metadata")
        return self._parse_record_header(data)

    @param("record", "integer", "nonnegative", desc="The record number of the saved record to download")
    @param("convert", "bool", desc="Convert readings to Gs or leave in internal ADC units")
    @return_type("basic_dict")
    def download_waveform(self, record, convert=True):
        """Download a saved waveform from the flash memory of the tile.

        This routine will temporarily pause measurement, download the given waveform
        and then resume measurement.  The waveform is returned from this function.
        If you want to save the waveform to a file, you should use the convenience
        function save_waveform.
        """

        record_count = self.count()
        if record >= record_count:
            raise ArgumentError("Invalid waveform index that does not exist", index=record, total_waveforms=record_count)

        download_size = 256 + 6*1024

        data = self.download_flash((record+1)*8192, download_size, message="Downloading Waveform")

        header = data[:256]
        event = self._parse_record_header(header)

        readings = data[256:]
        parsed = struct.unpack("<%dh" % (1024*3), readings)

        accel = {}
        accel['x'] = parsed[:1024]
        accel['y'] = parsed[1024:2048]
        accel['z'] = parsed[2048:]

        if convert:
            accel['x'] = [x*self._proxy.LSB_VALUE for x in accel['x']]
            accel['y'] = [y*self._proxy.LSB_VALUE for y in accel['y']]
            accel['z'] = [z*self._proxy.LSB_VALUE for z in accel['z']]

        event['waveform'] = accel

        return event

    @param("record", "integer", "nonnegative", desc="The record number of the saved record to download")
    @param("convert", "bool", desc="Convert readings to Gs or leave in internal ADC units")
    @param("out_path", "string", desc="The output path to save the waveform to as a csv")
    @param("stream", "bool", desc="Stream the waveform at highspeed rather than pulling it")
    def save_waveform(self, record, out_path, convert=True, stream=True):
        """Download a saved waveform from the flash memory of the tile.

        This routine will temporarily pause measurement, download the given waveform
        and then resume measurement.  The waveform is returned from this function.
        If you want to save the waveform to a file, you should use the convenience
        function save_waveform.

        If you pass stream=True (the default), the tile must be in streaming mode.
        """

        if stream:
            event = self.stream_waveform(record)
            event['sample_spacing'] = 1.0 / 3200. * 3.
            accel = event['data']
        else:
            event = self.download_waveform(record, convert=convert)
            accel = event['waveform']

        with open(out_path, "wb") as outfile:
            for i in xrange(0, len(accel['x'])):
                outfile.write("%f, %f, %f, %f\n" % (i*event['sample_spacing'], accel['x'][i], accel['y'][i], accel['z'][i]))

    @param("record", "integer", "nonnegative", desc="The record number of the saved record to download")
    @param("out_path", "string", desc="The output path to save the waveform to as a binary dump")
    def dump_waveform(self, record, out_path):
        """Dump the binary contents of a saved waveform from the tile."""


        with self._proxy.measurements_disabled():
            download_size = 2*4096
            data = self.download_flash((record+1)*8192, download_size, message="Downloading Waveform")

        with open(out_path, "wb") as outfile:
            outfile.write(data)

    def _parse_record_header(self, header):
        """Parse a record header and verify it is intact."""

        magic, version, length, unique_id, timestamp, compression, storage_flags = struct.unpack_from("<LHHLLBB2x", header)
        if magic != self.FLASH_RECORD_MAGIC or version != self.FLASH_RECORD_VERSION:
            raise HardwareError("Error parsing record header, magic or version is incorrect", magic=magic, version=version)

        shock_threshold, sampling_rate, flags, buffer_size, min_length, pretrigger_samples, decimation = struct.unpack_from("<HBBHHHB", header[20:])

        peak, length, deltax, deltay, deltaz = struct.unpack_from("<HHlll", header[32:])
        summary = {
            'peak_axis': _convert_axis(peak & 0b11),
            'peak': (peak >> 2) * self._proxy.LSB_VALUE,
            'deltav_x': deltax,
            'deltav_y': deltay,
            'deltav_z': deltaz,
            'length': length
        }

        _convert_event(summary)

        if timestamp == 0xFFFFFFFF:
            timestamp = None

        event = {}
        event['unique_id'] = unique_id
        event['timestamp'] = timestamp
        event['byte_length'] = length
        event['compression'] = compression
        event['flags'] = storage_flags
        event['min_event_length'] = min_length
        event['buffer_length'] = buffer_size
        event['shock_threshold_raw'] = shock_threshold
        event['shock_threshold'] = shock_threshold * self._proxy.LSB_VALUE
        event['pretrigger_samples'] = pretrigger_samples
        event['highpass_filter'] = bool(flags & (1 << 2))
        event['lowpass_filter'] = bool(flags & (1 << 3))
        event['reported'] = bool(flags & (1 << 0))
        event['summary_selection'] = (flags >> 5) & 0b111
        event['sampling_rate'] = self._proxy.SAMPLE_RATES[sampling_rate]
        event['decimation_factor'] = decimation
        event['sample_spacing'] = (1. / event['sampling_rate']) * decimation
        event['summary'] = summary

        return event

    @return_type("integer")
    def count(self):
        """Count how many events have been saved in flash.

        Returns:
            int: The number of readings stored in flash.
        """

        count, _limit, _erase_cycles = self.rpc(0x80, 0x30, result_format="LLL")
        return count

    @return_type("integer")
    def max_records(self):
        """Count how many events can be saved to flash.

        Returns:
            int: The number of readings that could fit in flash.
        """

        _count, limit, _erase_cycles = self.rpc(0x80, 0x30, result_format="LLL")
        return limit

    @return_type("integer")
    def erase_cycles(self):
        """Count how many times the flash memory has been erased

        Returns:
            int: The number of erase cycles completed
        """

        _count, _limit, erase_count = self.rpc(0x80, 0x30, result_format="LLL")
        return erase_count


@context("TestManager")
class TestManager(TileBusProxyPlugin):
    """A proxy plugin for injecting test data into the accelerometer tile."""

    @param("drop", 'bool', desc="drop samples received from the accelerometer")
    def set_drop_samples(self, drop):
        """Enable or disable data collection from the accelerometer."""

        error, = self.rpc(0x80, 0x05, int(drop), arg_format="B", result_format="L")

        if error != 0:
            raise HardwareError("Unable to set drop_samples flag", error_code=error, drop_samples=drop)

    @return_type("bool")
    def dropping_samples(self):
        """Return whether the accelerometer is currently measuring."""

        status = self._proxy._setup_manager.get_status()
        return not status['dropping_samples']

    @contextmanager
    def measurements_disabled(self):
        """Context manager that temporarily pauses data collection."""

        old_drop = self.dropping_samples()

        self.set_drop_samples(True)
        yield

        if not old_drop:
            self.set_drop_samples(False)

    @return_type('integer')
    def get_fifo_counter(self):
        """Read the number of times we have services the accelerometer's FIFO.

        This number should increase frequently when the accelerometer is recording
        data.

        :rtype: 32-bit unsigned integer
        """   
        int1_count, = self.rpc(0x80, 0x01, result_format="L")
        return int1_count

    def push_filters(self):
        """Save the current state of the dc blocking and lowpass filters."""

        err, = self.rpc(0x80, 0x23, 0, arg_format="B", result_format="L")
        if err:
            raise HardwareError("Error pushing filters", code=err)

    def pop_filters(self):
        """Save the current state of the dc blocking and lowpass filters."""

        err, = self.rpc(0x80, 0x23, 1, arg_format="B", result_format="L")
        if err:
            raise HardwareError("Error pushing filters", code=err)

    @return_type('integer')
    def get_overflow_counter(self):
        """Read the number of times data has overflowed from the accelerometer.

        This should be 0 if the tile is working correctly and servicing all 
        accelerometer FIFO interrupts quickly.

        :rtype: 32-bit unsigned integer
        """        
        int1_count, = self.rpc(0x80, 0x02, result_format="L")
        return int1_count

    @return_type("integer")
    def count_ringbuffer(self):
        """Count how many samples are in the tile's ring buffer."""

        status = self._proxy._setup_manager.get_status()
        return status['ringbuffer_counter']

    @param("x", 'integer', desc="x acceleration value in raw ADC units")
    @param("y", 'integer', desc="y acceleration value in raw ADC units")
    @param("z", 'integer', desc="z acceleration value in raw ADC units")
    @param("count", 'integer', desc="The number of repeat samples to push")
    def push_copies(self, x, y, z, count):
        """Push count copies of a single reading.

        This function is useful for pushing constant offset data
        to load up the tile's IIR bandpass filter.
        """

        error, = self.rpc(0x80, 0x0a, x, y, z, count, arg_format="hhhH", result_format="L")
        if error != 0:
            raise HardwareError("Unable to push a copies of a single reading", error_code=error)

    def push_many(self, data_list):
        """Push many readings into the accelerometer tile as quickly as possible.

        Up to 3 readings are pushed per RPC to maximum bandwidth utilization.

        Args:
            data_list (int[][3]): A list of 3-tuples of integers that will be pushed
                into the accelerometer.
        """

        i = 0

        # Push up to 3 readings at at time to the accelerometer
        while i < len(data_list):
            to_push = [x for x in data_list[i]]
            i += 1

            if len(data_list) > i:
                to_push += data_list[i]
                i += 1

            if len(data_list) > i:
                to_push += data_list[i]
                i += 1

            err, = self.rpc(0x80, 0x07, *to_push, arg_format="h"*len(to_push), result_format="L")
            if err != 0:
                raise HardwareError("Unable to push multiple readings", error_code=err)

    def push_z(self, data_list):
        """Push many readings to the z axis only as quickly as possible.

        The x and y axes are filled with zeros.

        Args:
            data_list: (int[]): A list of integers containing the z axis samples.
        """

        for i in xrange(0, len(data_list), 10):
            chunk = data_list[i:i+10]

            err, = self.rpc(0x80, 0x0d, *chunk, arg_format="h"*len(chunk), result_format="L")
            if err != 0:
                raise HardwareError("Unable to push multiple z axis samples", error_code=err)

    @return_type("integer")
    def sample_rate(self):
        """Return the sampling rate in hz.

        This function queries the current sampling rate
        from a config variable and converts the internal
        enum value to hertz.

        Returns:
            int: The configured tile sample rate in hertz.
        """

        config = self._proxy.config_manager()

        sample_rate_raw = config.get_variable(0x8002)
        sample_rate, = struct.unpack("<B", sample_rate_raw)

        converted = AccelProxy.SAMPLE_RATES.get(sample_rate, None)
        if converted is None:
            raise HardwareError("Unknown sample rate configured on tile", sample_rate=sample_rate)

        return converted

    @param("shape", "string", ["list", ["trapezoid", "constant"]], desc="The shape of shock to inject")
    @param("peak", "float", desc="The maximum peak value in g's")
    @param("axis", "string", desc="The axis to inject the shock event on")
    @param("duration", "float", desc="The duration of the peak of the event in ms excluding rise/fall time")
    @param("rise_time", "float", desc="The rise time from 0 to peak value.  This may be discarded depending on the shape.")
    @param("offset", "float", desc="A constant offset to apply to the axis of interest in g")
    def inject_data(self, shape, axis, peak, duration, rise_time, offset=0.0):
        """Inject a specifically shaped shock into the tile."""

        samples = self.build_waveform(shape, axis, peak, duration, rise_time, offset)

        # Optimization to significantly speed up pushing a large number of constant
        # readings.  If we are injecting onto the z axis, speed up the injection
        # by injecting 10 at a time instead of 3 at a time.
        if shape == 'constant':
            self.push_copies(*samples[0], count=len(samples))
        elif axis == 'z':
            self.push_z([x[2] for x in samples])
        else:
            self.push_many(samples)

    @param("constant", "float", desc="A constant offset to apply to the axis of interest in g")
    def settle(self, constant=1.0):
        """Settle the DC blocking filter for fixed period of time."""

        for _i in xrange(0, 8):
            self.inject_data('constant', 'z', constant, 1000, 0.0)

    def build_waveform(self, shape, axis, peak, duration, rise_time, offset=0.0):
        """Build a shock waveform for injecting into the tile.

        Args:
            shape (str): The shape of the waveform, currently supports trapezoid, constant and half-sine
            axis (str): x, y or z for the axis that we should inject the waveform on
            peak (float): The peak value of the shock in G's
            duration (float): The duration of the shock in ms
            rise_time (float): The rise and fall times of the shock in ms
            offset (float): A constant offset that can be applied to the axis to simulate gravity
        """

        sample_rate = self.sample_rate()
        sample_time = 1.0/sample_rate*1000.0

        index = _convert_axis(axis)
        samples = []

        if shape == 'trapezoid':
            rise_samples = int(rise_time / sample_time)
            top_samples = int(duration / sample_time)

            for i in xrange(0, rise_samples):
                value = int(peak / self._proxy.LSB_VALUE * (float(i) / rise_samples) + offset / self._proxy.LSB_VALUE)
                sample = [0, 0, 0]
                sample[index] = value
                samples.append(sample)

            for i in xrange(0, top_samples):
                value = int(peak / self._proxy.LSB_VALUE + offset / self._proxy.LSB_VALUE)
                sample = [0, 0, 0]
                sample[index] = value
                samples.append(sample)

            for i in xrange(0, rise_samples):
                value = int(peak / self._proxy.LSB_VALUE * (float(rise_samples - i - 1) / rise_samples) + offset / self._proxy.LSB_VALUE)
                sample = [0, 0, 0]
                sample[index] = value
                samples.append(sample)
        elif shape == 'constant':
            sample_count = int(duration / sample_time)

            sample = [0, 0, 0]
            sample[index] = int(peak / self._proxy.LSB_VALUE + offset / self._proxy.LSB_VALUE)

            for i in xrange(0, sample_count):
                samples.append(sample)
        else:
            raise ArgumentError("Unknown shock shape", shape=shape)

        return samples

    @param("axis", "string", desc="The axis to dump")
    @param("count", "integer", "nonnegative", desc="The number of samples to capture")
    @param("save", "path", desc="Output csv file to save")
    @return_type("list(string)")
    def peek_data(self, count=None, axis=None, save=None):
        """Peek at data from the tile's ring buffer.

        If count is None, this function downloads all data currently in the ring buffer,
        otherwise it downloads exactly count samples.

        If axis is None, this function downloads all three axes, otherwise it downloads only
        the specified axis.

        If save is not None, this function also produces a CSV file containing the
        returned samples.  It either has 1 or 3 columns.

        Returns:
            list: either a list of 3-tuples of a list of integers with the samples from
                the specified axis.
        """

        if count is None:
            count = self.count_ringbuffer()

        if axis is None:
            readings = self.dump_all(count)
        else:
            readings = self.dump_axis(axis, count)

        if save is not None:
            with open(save, "wb") as outfile:
                for reading in readings:
                    if isinstance(reading, (int, long)):
                        reading = [reading]

                    reading = [str(x) for x in reading]
                    outfile.write(", ".join(reading) + '\n')

        return readings

    def dump_all(self, count):
        """Pop all data from the ring buffer and return it as a list of 3-tuples."""

        readings = []

        for i in xrange(0, count, 3):
            chunk = min(count - i, 3)
            reading_chunk = self.rpc(0x80, 0x08, chunk, len(readings), arg_format="HH", result_format="hhh"*chunk)

            for j in xrange(0, chunk):
                reading = reading_chunk[3*j:3*(j+1)]
                readings.append(reading)

        return readings

    def dump_axis(self, axis, count):
        """Accumulate and dump count samples from the accelerometer tile."""

        axis = _convert_axis(axis)

        out_readings = []

        while len(out_readings) < count:
            chunk = min(count - len(out_readings), 10)
            res = self.rpc(0x80, 0x0c, chunk, axis, len(out_readings), arg_format="HHH", result_type=(0, True))

            reading_buf = res['buffer']
            readings = struct.unpack("<" + ("h"*(len(reading_buf)//2)), reading_buf)
            out_readings += readings

        return out_readings

    @annotated
    def clear_ringbuffer(self):
        """Clear any stored ringbuffer readings."""

        err, = self.rpc(0x80, 0x0b, result_format="L")
        if err != 0:
            raise HardwareError("Unable to clear ringbuffer", error_code=err)

    @annotated
    def clear_state(self):
        """Clear internal ringbuffer in tile and all filter state."""

        err, = self.rpc(0x80, 0x09, result_format="L")
        if err != 0:
            raise HardwareError("Unable to clear all readings", error_code=err)


@context("SetupManager")
class SetupManager(TileBusProxyPlugin):
    """A proxy plugin for setting up the accelerometer tile.

    This manager allows configuring the shock threshold and other parameters
    about the tile.
    """

    STATE_TABLE = {
        0: "idle",
        1: "triggered",
        2: "accumulating",
        3: "retriggered",
        4: "reporting"
    }

    TILE_STATE_TABLE = {
        0: "initializing",
        1: "capturing",   # Capture mode just means that recording could happen, it doesn't mean that it is happening
        2: "streaming"
    }

    REPORT_TYPE_TABLE = {
        0: "nothing",
        1: "summary",
        2: "id_only"
    }

    SUMMARY_TYPE_TABLE = {
        0: "peak_g",
        1: "delta_v"
    }

    @return_type("basic_dict")
    def get_config(self):
        """Get the configured state of the accelerometer tile."""

        shock_threshold, sample_rate, flags, sample_length, min_event, pretrigger_length, decimation, report_type = self.rpc(0x80, 0x21, result_format="HBBHHHBB")

        config = {
            'shock_threshold': shock_threshold * self._proxy.LSB_VALUE,
            'sample_rate': AccelProxy.SAMPLE_RATES.get(sample_rate, None),
            'report_shocks': bool(flags & (1 << 0)),
            'report_type': SetupManager.REPORT_TYPE_TABLE.get(report_type, 'unknown'),
            'save_waveforms': bool(flags & (1 << 1)),
            'dc_block_enabled': bool(flags & (1 << 2)),
            'lowpass_enabled': bool(flags & (1 << 3)),
            'event_summary': SetupManager.SUMMARY_TYPE_TABLE.get(flags >> 5, 'unknown'),
            'ringbuffer_length': sample_length,
            'min_event_length': min_event,
            'pretrigger_samples': pretrigger_length,
            'decimation_rate': decimation
        }

        return config

    @param("threshold", "float", desc="the threshold to set in G's")
    def shock_threshold(self, threshold):
        """Temporarily set the shock threshold."""

        threshold = int(threshold / self._proxy.LSB_VALUE)

        error, = self.rpc(0x80, 0x22, threshold, result_format="L")
        if error != 0:
            raise HardwareError("Unable to configure shock threshold", error_code=error)

    @param("report", "bool", desc="whether to report shocks to the controller")
    def report_shocks(self, report):
        """Enable/disable reporting shocks to the controller."""

        error, = self.rpc(0x80, 0x0e, int(report), arg_format="B", result_format="L")
        if error != 0:
            raise HardwareError("Unable to configure shock reporting", error_code=error)

    @param("enable", 'bool', desc="True to enable, False to disable")
    def dc_block(self, enable):
        """Enable or disable dc blocking filter."""

        error, = self.rpc(0x80, 0x15, int(enable), arg_format="B", result_format="L")

        if error != 0:
            raise HardwareError("Unable to configure DC blocking filter", error_code=error)

    @param("enable", 'bool', desc="True to enable, False to disable")
    def save_waveforms(self, enable):
        """Enable or disable waveform saving."""

        error, = self.rpc(0x80, 0x33, int(enable), arg_format="B", result_format="L")

        if error != 0:
            raise HardwareError("Unable to configure waveform saving", error_code=error)

    @annotated
    def stop_recording(self):
        """Turn off the accelerometer and enter a low power sleep state."""

        error, = self.rpc(0x80, 0x35, result_format="L")
        if error != 0:
            raise HardwareError("Unable to stop recording", error_code=error)

    @annotated
    def start_recording(self):
        """Turn on the accelerometer and begin recording shocks."""

        error, = self.rpc(0x80, 0x36, result_format="L")
        if error != 0:
            raise HardwareError("Unable to start recording", error_code=error)

    @return_type("basic_dict")
    def get_status(self):
        """Get event counters and status flags from tile."""

        last_err, shock_counter, tile_state, state, flags, x, y, z = self.rpc(0x80, 0x06, result_format="LLBxBB3h2x")

        status = {
            'shock_counter': shock_counter,
            'tile_state': self.TILE_STATE_TABLE.get(tile_state, 'unknown'),
            'trigger_state': self.STATE_TABLE.get(state, "unknown"),
            'recording': bool(flags & (1 << 0)),
            'should_record': bool(flags & (1 << 1)),
            'settled': bool(flags & (1 << 2)),
            'dropping_samples': bool(flags & (1 << 3)),
            'streaming': bool(flags & (1 << 4)),
            'clearing_flash': bool(flags & (1 << 5)),
            'force_triggering': bool(flags & 1 << 6),
            'last_error': last_err,
            'last_sample': (x, y, z)
        }

        return status

    @annotated
    def admin_reset(self):
        """Clear all stored events stored in the accel tile."""

        err, = self.rpc(0x80, 0x31, result_format="L")
        if err:
            raise HardwareError("Error clearing events from tile", error_code=err)


@context("CalibrationManager")
class CalibrationManager(TileBusProxyPlugin):
    """Allows for testing and calibrating the accelerometer."""

    @return_type("list(float)")
    @param("sample_count", "integer")
    def static_offset(self, sample_count=128):
        """Measure the average acceleration vector on each axis"""

        samples = []
        lengths = []

        for _i in xrange(0, sample_count):
            x, y, z = self._proxy.last_sample()
            samples.append((x, y, z))

        for i in xrange(0, 3):
            axis = [float(x[i]) for x in samples]
            lengths.append(sum(axis) / sample_count)

        return lengths

    @param("axis", "string", desc="The axis to dump")
    @param("sample_count", "integer", "nonnegative", desc="The number of samples to capture")
    @return_type("float")
    def measure_noise(self, axis, sample_count=1024):
        """Estimate the standard deviation of the noise on the given axis."""

        samples = []

        axis = _convert_axis(axis)

        for _i in xrange(0, sample_count):
            data = self._proxy.last_sample()
            samples.append(data[axis])

        mean = float(sum(data)) / len(data)

        std = 0.0

        for val in data:
            std += (val - mean)*(val - mean)

        std /= len(data)
        return math.sqrt(std)

    @classmethod
    def _argmax(cls, arr):
        imax = 0
        max_val = arr[0]

        for i in xrange(1, len(arr)):
            if arr[i] > max_val:
                imax = i
                max_val = arr[i]

        return imax

    @annotated
    @param("sample_count", "integer")
    def calibrate_axis(self, sample_count=512):
        """Determine the sensitivity and offset of an axis.

        This routine measures the 1G field of gravity in two different
        orientations and calculates the offset (in LSB) and scale factor
        for the given axis.
        """

        raw_input("Place the axis in one orientation vertically and then press return")
        axis1 = self.static_offset(sample_count=sample_count)

        raw_input("Flip the unit over and press return")
        axis2 = self.static_offset(sample_count=sample_count)

        diffs = [abs(axis1[i] - axis2[i]) for i in xrange(0, 3)]

        axis = self._argmax(diffs)
        print("Detected calibration on %s axis" % _convert_axis(axis))

        diff = diffs[axis]
        lsb = 2.0 / diff

        print("\nCalibration:")
        print(" - LSB: %.1f mG/lsb" % (lsb*1000,))

    @docannotate
    def get_calibration(self):
        """Get the current calibration information saved in the tile.

        Returns:
            basic_dict: The calibration information
        """

        gain_x, gain_y, gain_z, off_x, off_y, off_z = self.rpc(0x80, 0x42, result_format="LLLhhh2x")

        return {
            "gain_x": gain_x / 65536.,
            "gain_y": gain_y / 65536.,
            "gain_z": gain_z / 65536.,
            'offset_x': off_x * self._proxy.LSB_VALUE,
            'offset_y': off_y * self._proxy.LSB_VALUE,
            'offset_z': off_z * self._proxy.LSB_VALUE 
        }

    @docannotate
    def set_calibration(self, gain_x, gain_y, gain_z, off_x, off_y, off_z):
        """Set the tile calibration information.

        Args:
            gain_x (float): The gain adjustment for the x axis.
            gain_y (float): The gain adjustment for the y axis.
            gain_z (float): The gain adjustment for the z axis.
            off_x (float): The offset to be subtracted from the x axis.
            off_y (float): The offset to be subtracted from the y axis.
            off_z (float): The offset to be subtracted from the z axis.
        """

        gain_x = int(gain_x * 65536)
        gain_y = int(gain_y * 65536)
        gain_z = int(gain_z * 65536)
        off_x = int(off_x / self._proxy.LSB_VALUE)
        off_y = int(off_y / self._proxy.LSB_VALUE)
        off_z = int(off_z / self._proxy.LSB_VALUE)

        err, = self.rpc(0x80, 0x40, gain_x, gain_y, gain_z, off_x, off_y, off_z, arg_format="LLLhhh2x", result_format="L")
        if err:
            raise HardwareError("Error setting calibration", error_code=err)

    @docannotate
    def persist_calibration(self):
        """Save the current calibration persistently.

        This function also stores a unique guid and the current timestamp
        with the data so that we always know when the calibration was performed.

        Returns:
            str: The guid that was saved with the calibration data.
        """

        guid = uuid.uuid4()
        now = datetime.datetime.utcnow()
        ref = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)

        secs = (now - ref).total_seconds()

        err, = self.rpc(0x80, 0x41, secs, guid.bytes_le, arg_format="L16s", result_format="L")
        if err:
            raise HardwareError("Error persisting calibration", error_code=err)

        return str(guid)

    @docannotate
    def calibration_info(self):
        """Get the calibration date and serial number of the last calibration.

        Returns:
            basic_dict: a dictionary with calibration_time, serial_number 
                members.
        """

        timestamp, guid_bytes = self.rpc(0x80, 0x43, result_format="L16s")

        guid = uuid.UUID(bytes_le=guid_bytes)
        ref = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        delta = datetime.timedelta(seconds=timestamp)

        calib_date = ref + delta

        if delta == 0:
            return None

        return {
            'calibration_time': calib_date,
            'serial_number': guid
        }

def _convert_axis(in_axis):
    """Convert a numeric axis identifier to a string and back."""

    axes = {
        0: 'x',
        1: 'y',
        2: 'z'
    }

    reverse_axes = {
        'x': 0,
        'y': 1,
        'z': 2
    }

    if isinstance(in_axis, (str, unicode)):
        result = reverse_axes.get(in_axis, None)
    else:
        result = axes.get(in_axis, None)

    if result is None:
        raise HardwareError("Invalid axis code", axis=in_axis)

    return result


def _convert_event(event):
    """Convert an every summary to conventional SI units."""

    event['deltav_x'] /= 65536.0
    event['deltav_y'] /= 65536.0
    event['deltav_z'] /= 65536.0

    if event['length'] > 0:
        event['average_x'] = event['deltav_x'] / event['length'] / 9.80665 * 1000.
        event['average_y'] = event['deltav_y'] / event['length'] / 9.80665 * 1000.
        event['average_z'] = event['deltav_z'] / event['length'] / 9.80665 * 1000.

        avg = (event['average_x'], event['average_y'], event['average_z'])
        avg_length = math.sqrt((avg[0]*avg[0] + avg[1]*avg[1] + avg[2]*avg[2]))
        avg_dir = (avg[0] / avg_length, avg[1] / avg_length, avg[2] / avg_length)

        # Convert to orientation of shock
        theta = math.acos(avg_dir[2])*180/math.pi

        if avg_dir[0] == 0.0:
            phi = math.pi / 2.0
        else:
            phi = math.atan(avg_dir[1] / avg_dir[0])

        phi *= 180 / math.pi

        event['theta'] = theta
        event['phi'] = phi


class HeatshrinkDecoder(object):
    def __init__(self, window_bits=8, lookahead_bits=4):
        self.window_bits = window_bits
        self.lookahead_bits = lookahead_bits

        self.window = bytearray(2 ** self.window_bits)
        self.window_head = 0
        self.output = bytearray([])

    def decode(self, data):
        """Decode heatshrink compressed data."""

        try:
            import bitstring
        except ImportError:
            raise ExternalError("You must have the bitstring package installed from pip to use this", suggestion="pip install bitstring")
        
        input_buffer = bitstring.ConstBitStream(data)

        while len(input_buffer) - input_buffer.pos >= 8:
            is_literal = input_buffer.read("bool")
            if is_literal:
                val = input_buffer.read('uint:8')
                self._emit_byte(val)
            elif (len(input_buffer) - input_buffer.pos) >= (self.window_bits + self.lookahead_bits):
                index = input_buffer.read("uintbe:%d" % self.window_bits)
                count = input_buffer.read("uint:%d" % self.lookahead_bits)

                index += 1
                count += 1

                for _i in xrange(0, count):
                    neg_index = self.window_head - index

                    val = self.window[neg_index]
                    self._emit_byte(val)
            else:
                break

    def _emit_byte(self, value):
        self.output.append(value)
        self.window[self.window_head] = value
        self.window_head += 1

        if self.window_head == len(self.window):
            self.window_head = 0
