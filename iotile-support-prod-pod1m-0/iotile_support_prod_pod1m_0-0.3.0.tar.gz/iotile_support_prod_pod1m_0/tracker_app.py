"""An IOTileApp Plugin that operates a POD-1M as a shock/environmental tracker."""

import sys
import os
import shutil
import json
import msgpack
from datetime import datetime
from iotile.core.hw import IOTileApp
from iotile.core.dev.config import ConfigManager
from iotile.core.hw.reports import IndividualReadingReport, FlexibleDictionaryReport
from iotile.core.hw.reports.report import IOTileEvent
from iotile.core.dev.semver import SemanticVersionRange
from iotile.core.exceptions import HardwareError, ArgumentError
from iotile.cloud import IOTileCloud
from iotile.sg import DataStream
from typedargs.annotate import context, docannotate
from typedargs import type_system, iprint


# Physical Constants
M_S__TO_IN_S = 39.3700787
G_CONST = 9.80665


@context("LogisticsTracker")
class LogisticsTracker(IOTileApp):
    """A shipment tracker with support for shock, vibe and environmental logging.

    This app requires a POD-1M device with a properly configured shipment
    tracker sensorgraph for all functionality to work as intended.  This app
    provides equivalent functionality to the IOTile Companion device page for
    the shipment tracker.
    """

    APP_TAG = 2049
    APP_VERSION = "^1.0.0"
    START_STREAM = 'system buffered 1536'
    END_STREAM = 'system buffered 1537'

    WAVEFORM_STREAMER = 0x100

    ACCEL_STREAM = "output 32"
    TEMP_STREAM = "output 35"
    HUM_STREAM = "output 34"
    PRESS_STREAM = "output 33"

    HUM_RT_STREAM = "unbuffered 15"
    TEMP_RT_STREAM = "unbuffered 25"
    PRESS_RT_STREAM = "unbuffered 22"
    SHOCKS_RT_STREAM = "unbuffered 18"

    ACCEL_ADDRESS = 12

    @classmethod
    def MatchInfo(cls):
        """Return the list of app types that we automatch."""

        return [(cls.APP_TAG, SemanticVersionRange.FromString(cls.APP_VERSION), 50)]

    @classmethod
    def AppName(cls):
        """Return our name to allow users to explicitly specify us."""

        return "logistics_tracker"

    def suppress_output(self):
        """Context manager that will not show interactive output."""

        class _Suppressor(object):  #pylint:disable=too-few-public-methods; This is an internal class
            old_interactive = False
            def __enter__(self):
                self.old_interactive = type_system.interactive
                type_system.interactive = False

            def __exit__(self, *args):
                type_system.interactive = self.old_interactive

        return _Suppressor()

    @docannotate
    def trip_info(self):
        """Get information on the current trip, if there is one.

        This function will determine if there is a trip currently
        in progress and if so, when it started.  If there is a finished
        trip stored in the tracker, this function will also determine
        the stop date.

        There are 4 potential trip statuses that you can find with
        this function:
            'not started': The device is waiting for a trip to start
            'in progress': The device is currently in the middle of
                a trip
            'finished': The device has recorded one complete trip
                with a start and end date.
            'corrupted': The device is in a corrupted state where there
                is an end trip event but no corresponding start trip
                event.
            'multiple trips': The device is in an unsupported state
                where data from more than one trip is stored.

        Returns:
            basic_dict: Information about the trip including whether it
                is in progress or finished.
        """

        sgraph = self._hw.controller().sensor_graph()

        with self.suppress_output():
            trip_starts = sgraph.download_stream('system buffered 1536')
            trip_ends = sgraph.download_stream('system buffered 1537')
            _pause_resumes = sgraph.download_stream('system buffered 1538')

            is_running = sgraph.inspect_virtualstream('constant 1')

        info = _determine_trip_status(trip_starts, trip_ends)
        info['recording_data'] = bool(is_running)
        return info

    @docannotate
    def admin(self):
        """Access the protected administrative interface of the device.

        The admin interface should not be necessary in normal usage.  It
        exists for debugging purposes and other engineering needs.  If you
        find yourself using it repeatedly and you are not an Arch developer,
        you should probably report a bug and describe what you are trying 
        to accomplish.
        """

        return TrackerAdmin(self)

    @docannotate
    def start_trip(self):
        """Start a trip.

        This routine will mark the start of the trip and begin recording
        data.  You can stop a trip by calling stop_trip().  You can 
        pause and resume data recording during a trip by calling
        pause_trip() or resume_trip().
        """

        info = self.trip_info()
        if info['trip_status'] != 'not started':
            raise HardwareError("You may only start a trip once without resetting the tracker", **info)

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input('system input 1536', _current_timestamp())
        self.resume_trip()

    @docannotate
    def end_trip(self):
        """End a trip that is currently in progress.

        This routine will stop data recording and mark the end of the trip.
        You can only call it when a trip is in progress.
        """

        info = self.trip_info()
        if info['trip_status'] != 'in progress':
            raise HardwareError("You must start a trip before you can stop a trip", **info)

        if info['recording_data']:
            self.pause_trip()

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input('system input 1537', _current_timestamp())

    @docannotate
    def resume_trip(self):
        """Resume recording data during a trip.

        You may only call resume trip after a trip has started and recording
        has been paused.  Calling resume trip when recording has already
        been resumed will throw an exception.
        """

        info = self.trip_info()
        if info['trip_status'] != 'in progress' or info['recording_data'] is not False:
            raise HardwareError("You may only resume a trip when there is a trip to resume", **info)

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input('system input 1538', 1)

    @docannotate
    def pause_trip(self):
        """Resume recording data during a trip.

        You may only call resume trip after a trip has started and recording
        has been paused.  Calling resume trip when recording has already
        been resumed will throw an exception.
        """

        info = self.trip_info()
        if info['trip_status'] != 'in progress' or info['recording_data'] is not True:
            raise HardwareError("You may only pause a trip when it is currently recording data", **info)

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input('system input 1538', 0)

    @docannotate
    def upload_trip(self, save=None, clean=False, dryrun=False, acknowledge=True):
        """Upload a finished trip to the cloud.

        This function will download all data from the device and upload it to
        IOTile.cloud.  If you pass dryrun=True, no data will actually be
        uploaded.  If you pass a path to a folder in the save parameter, all
        files that would be uploaded to the cloud will be saved to that
        folder.  This can be combined with dryrun only download data and not
        upload it to the cloud.

        Args:
            save (str): The path to a folder where all data should be saved
                before uploading.  This is optional, if you don't specify it
                no data will be saved.
            dryrun (bool): Download the data from the device but do not upload
                it to the cloud.  This is useful for testing and for
                downloading data only when combined with the save parameter.
            clean (bool): When combined with save, this will clear all old files
                from the directory specified in save.  Otherwise it has no effect.
            acknowledge (bool): Acknowledge received readings from iotile.cloud
                before downloading new data.
        """

        info = self.trip_info()
        if info['trip_status'] != 'finished':
            raise HardwareError("You must finish a trip first before calling upload_trip", trip_status=info['trip_status'])

        if save is not None:
            if os.path.exists(save) and not os.path.isdir(save):
                raise ArgumentError("You passed a save directory that exists but is not a directory", directory=save)

            if os.path.exists(save) and clean:
                iprint("Cleaning folder at: %s" % save)
                shutil.rmtree(save)

            if not os.path.exists(save):
                os.makedirs(save)

        reports = self._download_trip_reports(acknowledge)
        waves = self._download_waveforms()

        if save:
            for i, report in enumerate(reports):
                out_path = os.path.join(save, "report_%d_%s.bin" % (i, report.received_time.isoformat().replace(':', '-')))
                with open(out_path, "wb") as outfile:
                    outfile.write(report.encode())

            for wave in waves:
                out_path = os.path.join(save, "waveform_%08X.json" % wave['unique_id'])
                with open(out_path, "w") as out_file:
                    json.dump(wave, out_file, indent=4)

        cloud = IOTileCloud()

        uuid = self._device_id
        streamer = self.WAVEFORM_STREAMER

        try:
            last_uploaded = cloud.highest_acknowledged(uuid, streamer)
        except ArgumentError:
            last_uploaded = 0

        # Make sure to sort the waveforms we got by time so they are in the right order
        # We are technically sorting by flash storage index but since flash is used
        # sequentially, this is also sorting by time.
        waves = sorted(waves, key=lambda x: x['unique_id'])
        events = [_create_waveform_event(x) for x in waves if x['unique_id'] > last_uploaded]
        wave_report = FlexibleDictionaryReport.FromReadings(uuid, [], events, sent_timestamp=0xFFFFFFFF, received_time=datetime.utcnow())

        if save:
            out_path = os.path.join(save, "waveform_report.mp")
            with open(out_path, "wb") as outfile:
                outfile.write(wave_report.encode())

            out_path = os.path.join(save, "waveform_report.json")
            with open(out_path, "w") as outfile:
                data = msgpack.unpackb(wave_report.encode())
                json.dump(data, outfile, indent=4)

        if dryrun:
            return

        iprint("Ignoring %d old waveforms" % (len(events) - len(waves)))
        iprint("Uploading %d reports and %d waveforms to %s" % (len(reports), len(events), ConfigManager().get('cloud:server')))

        # Important for correct cloud processing, waveforms must be uploaded first before reports
        if len(events) > 0:
            iprint(" - uploading waveforms")
            cloud.upload_report(wave_report)
        else:
            iprint(" - no new waveforms to upload")

        for i, report in enumerate(reports):
            iprint(" - uploading report %d" % (i+1,))
            cloud.upload_report(report)

        iprint(" - finished")

    @docannotate
    def overview(self):
        """Get an overview of the current status of the tracker.

        This function will query all relevant high level information about the
        tracker and present it as a single dictionary.  It determines:

        - whether the tracker is currently in a trip
        - how many shocks it has seen
        - information on the largest shocks seen since the trip began

        Returns:
            basic_dict: A dictionary of information about the current status of
                the tracker.
        """

        accel = self._hw.get(self.ACCEL_ADDRESS)
        status = accel.setup_manager().get_status()

        trip_info = self.trip_info()

        overview = {}
        overview['trip_status'] = trip_info['trip_status']
        overview['shocks_seen'] = status['shock_counter']
        overview['recording_data'] = trip_info['recording_data']

        if overview['shocks_seen'] > 0:
            overview['shocks_peakg'] = _format_shock(accel.get_shock('max_g'))
            overview['shocks_peakdv'] = _format_shock(accel.get_shock('max_dv'))
            overview['shocks_last'] = _format_shock(accel.get_shock('last'))
        else:
            overview['shocks_peakg'] = None
            overview['shocks_peakdv'] = None
            overview['shocks_last'] = None

        return overview

    @docannotate
    def watch_realtime(self):
        """Print out realtime information as it comes from the device.

        This will continually update the displayed realtime information once
        per second until you stop it with Ctrl-C.
        """

        temp_tag = DataStream.FromString(self.TEMP_RT_STREAM).encode()
        hum_tag = DataStream.FromString(self.HUM_RT_STREAM).encode()
        press_tag = DataStream.FromString(self.PRESS_RT_STREAM).encode()
        shocks_tag = DataStream.FromString(self.SHOCKS_RT_STREAM).encode()

        try:
            self._hw.enable_streaming()
            press = 0.0
            temp = 0.0
            shock_count = 0
            hum = 0.0
            last_shock = ""

            for report in self._hw.iter_reports(blocking=True):
                if not isinstance(report, IndividualReadingReport):
                    continue

                reading = report.visible_readings[0]
                if reading.stream == temp_tag:
                    temp = reading.value / 100.0
                elif reading.stream == hum_tag:
                    hum = reading.value / 1024.
                elif reading.stream == press_tag:
                    press = reading.value / 100.
                elif reading.stream == shocks_tag:
                    if reading.value != shock_count:
                        last_shock = _format_shock(self._hw.get(12).last_shock())

                    shock_count = reading.value

                sys.stdout.write("\r| Shocks: %04d | Last Shock: %21s | Temp: % 02.1f C | Pressure: %04.0f mbar | H: %02.1f %%RH |" % (shock_count, last_shock, temp, press, hum))
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("")

    def _download_trip_reports(self, acknowledge):
        downloader = self._hw.app(name='cloud_uploader')

        iprint("Downloading trip reports from device...")
        reports = downloader.download(trigger=0, acknowledge=acknowledge)

        for report in reports:
            iprint(" - received report from streamer %d with %d readings" % (report.origin_streamer, len(report.visible_readings)))

        iprint(" - finished.")

        return reports

    def _download_waveforms(self):
        """Download the top 100 stored waveforms in the POD1-M."""

        accel = self._hw.get(12)
        waveman = accel.waveform_manager()

        waveman.enter_streaming_mode()

        try:
            waveman.sort_waveforms()
            waves = waveman.stream_sorted_waveforms()
        finally:
            waveman.leave_streaming_mode()

        return waves


@context("TrackerAdmin")
class TrackerAdmin(object):
    def __init__(self, app):
        self.app = app

    @docannotate
    def clear_trip(self):
        """Clear all data on the POD and prepare for another trip.

        This routine will delete all information stored on the POD and return
        it to 'not started' status so that you can begin another trip.  If you
        call this function before uploading data you will lose all data on the
        device.
        """

        # FIXME: Until we support the sensor graph with this input 2 turned on
        # call all of the RPCs manually.

        status = self.app.trip_info()
        if status['trip_status'] == 'in progress':
            raise HardwareError("You cannot reset a POD while it is in a trip, please end the trip first.")

        setup = self.app._hw.get(12).setup_manager()
        sgraph = self.app._hw.controller().sensor_graph()

        setup.admin_reset()
        sgraph.clear()

    @docannotate
    def reboot(self):
        """Forcibly reboot the device.

        This reboots the device and causes it to reinitialize itself. This will
        not delete any data from the device and should not be generally necessary
        to do ever.  It exists only to provide a quick way to fix any weirdness
        that you observe while using the device.

        If you need to use this function you should also probably also report
        a bug and describe what behavior you were seeing from the device.
        """

        print("Rebooting, this will take about 5 seconds...")

        with self.app.suppress_output():
            self.app._hw.controller().reset()


def _format_shock(shock):
    """Format a shock into X G, Y in/s."""

    peak = shock['peak']
    peak_axis = shock['peak_axis']
    max_dv = max(abs(shock['deltav_x']), max(abs(shock['deltav_y']), abs(shock['deltav_z'])))

    max_dv *= M_S__TO_IN_S

    return "%.1f G, %.2f in/s on %s" %(peak, max_dv, peak_axis)

def _current_timestamp():
    """Return the number of seconds since the unix epoch."""

    now = datetime.utcnow()
    return int((now - datetime(1970, 1, 1)).total_seconds())


def _parse_timestamp(seconds):
    """Turn the number of seconds since the epoch into a datetime."""

    return datetime.utcfromtimestamp(float(seconds))


def _determine_trip_status(start_events, end_events):
    """Determine a trip status given a list of start and end events."""

    if len(start_events) == 0 and len(end_events) == 0:
        return {
            'trip_status': 'not started',
            'trip_start': None,
            'trip_end': None
        }
    elif len(start_events) == 0 and len(end_events) > 0:
        return {
            'trip_status': 'corrupted',
            'trip_start': None,
            'trip_end': _parse_timestamp(end_events[-1].value)
        }
    elif len(start_events) > 1 or len(end_events) > 1:
        return {
            'trip_status': 'multiple trips',
            'trip_start': None,
            'trip_end': None
        }
    elif len(start_events) == 1 and len(end_events) == 0:
        return {
            'trip_status': 'in progress',
            'trip_start': _parse_timestamp(start_events[0].value),
            'trip_end': None
        }

    return {
        'trip_status': 'finished',
        'trip_start': _parse_timestamp(start_events[0].value),
        'trip_end': _parse_timestamp(end_events[0].value)
    }


def _time_above_threshold(data, thresh, sampling_rate):
    """Return the number of ms that a given time series is above a threshold."""

    max_count = 0
    curr_count = 0
    above = False
    last_sample = 0.0

    for sample in data:
        if above is False and abs(sample) >= thresh:
            above = True
            curr_count = 0
        elif above:
            curr_count += 1
            if abs(sample) < thresh or last_sample*sample < 0.0:
                above = False
                if curr_count > max_count:
                    max_count = curr_count

        last_sample = sample

    if above and curr_count > max_count:
        max_count = curr_count

    return max_count / sampling_rate * 1000.0


def _delta_v(data, thresh, sampling_rate):
    """Calculate the largest delta_v for the timeseries."""

    max_dv = 0
    curr_dv = 0
    above = False
    last_sample = 0.0

    for sample in data:
        if above is False and abs(sample) >= thresh:
            above = True
            curr_dv = sample
        elif above:
            curr_dv += sample
            if abs(sample) < thresh or last_sample*sample < 0.0:
                above = False
                if abs(curr_dv) > abs(max_dv):
                    max_dv = curr_dv

        last_sample = sample

    if above and abs(curr_dv) > abs(max_dv):
        max_dv = curr_dv

    return max_dv*G_CONST / sampling_rate


def _abslist(indata):
    return [abs(x) for x in indata]


def _summarize_waveform(wave, thresh, sampling_rate):
    """Create summary data for a waveform."""

    x_data = wave['data']['x']
    y_data = wave['data']['y']
    z_data = wave['data']['z']

    max_x = max(_abslist(x_data))
    max_y = max(_abslist(y_data))
    max_z = max(_abslist(z_data))

    max_g = max(max_x, max(max_y, max_z))

    if max_g == max_x:
        axis = 'x'
    elif max_g == max_y:
        axis = 'y'
    else:
        axis = 'z'

    dur_x = _time_above_threshold(x_data, thresh, sampling_rate)
    dur_y = _time_above_threshold(y_data, thresh, sampling_rate)
    dur_z = _time_above_threshold(z_data, thresh, sampling_rate)

    dur = max(dur_x, max(dur_y, dur_z))

    return {
        'peak': max_g,
        'axis': axis,
        'duration': dur,
        'delta_v_x': _delta_v(x_data, thresh, sampling_rate),
        'delta_v_y': _delta_v(y_data, thresh, sampling_rate),
        'delta_v_z': _delta_v(z_data, thresh, sampling_rate)
    }


def _create_waveform_event(wave, sampling_rate=3200 / 3., threshold=1.0):
    """Create an IOTileEvent object for a waveform."""

    stream = DataStream.FromString(LogisticsTracker.ACCEL_STREAM).encode()

    data = {
        'acceleration_data': {
            'x': wave['data']['x'],
            'y': wave['data']['y'],
            'z': wave['data']['z']
        },

        'sampling_rate': sampling_rate,  # We sample at 1066 Hz (3200 hz with 3x decimation)
        'crc_code': wave['crc32_value']
    }

    summary = _summarize_waveform(wave, threshold, sampling_rate)

    return IOTileEvent(wave['timestamp'], stream, summary, data, reading_id=wave['unique_id'])
