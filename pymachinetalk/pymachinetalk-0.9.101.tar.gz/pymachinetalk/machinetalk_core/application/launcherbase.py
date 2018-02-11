import zmq
import threading
import uuid
from fysom import Fysom
from ..common.rpcclient import RpcClient
from ..application.launchersubscribe import LauncherSubscribe

import machinetalk.protobuf.types_pb2 as pb
from machinetalk.protobuf.message_pb2 import Container


class LauncherBase(object):
    def __init__(self, debuglevel=0, debugname='Launcher Base'):
        self.debuglevel = debuglevel
        self.debugname = debugname
        self._error_string = ''
        self.on_error_string_changed = []

        # Launchercmd
        self._launchercmd_channel = RpcClient(debuglevel=debuglevel)
        self._launchercmd_channel.debugname = '%s - %s' % (self.debugname, 'launchercmd')
        self._launchercmd_channel.on_state_changed.append(self._launchercmd_channel_state_changed)
        self._launchercmd_channel.on_socket_message_received.append(self._launchercmd_channel_message_received)
        # more efficient to reuse protobuf messages
        self._launchercmd_rx = Container()
        self._launchercmd_tx = Container()

        # Launcher
        self._launcher_channel = LauncherSubscribe(debuglevel=debuglevel)
        self._launcher_channel.debugname = '%s - %s' % (self.debugname, 'launcher')
        self._launcher_channel.on_state_changed.append(self._launcher_channel_state_changed)
        self._launcher_channel.on_socket_message_received.append(self._launcher_channel_message_received)
        # more efficient to reuse protobuf messages
        self._launcher_rx = Container()

        # callbacks
        self.on_launchercmd_message_received = []
        self.on_launcher_message_received = []
        self.on_state_changed = []

        # fsm
        self._fsm = Fysom({'initial': 'down',
                          'events': [
                            {'name': 'connect', 'src': 'down', 'dst': 'trying'},
                            {'name': 'launchercmd_up', 'src': 'trying', 'dst': 'syncing'},
                            {'name': 'disconnect', 'src': 'trying', 'dst': 'down'},
                            {'name': 'launchercmd_trying', 'src': 'syncing', 'dst': 'trying'},
                            {'name': 'launcher_up', 'src': 'syncing', 'dst': 'synced'},
                            {'name': 'disconnect', 'src': 'syncing', 'dst': 'down'},
                            {'name': 'launcher_trying', 'src': 'synced', 'dst': 'syncing'},
                            {'name': 'launchercmd_trying', 'src': 'synced', 'dst': 'trying'},
                            {'name': 'disconnect', 'src': 'synced', 'dst': 'down'},
                          ]})

        self._fsm.ondown = self._on_fsm_down
        self._fsm.onafterconnect = self._on_fsm_connect
        self._fsm.ontrying = self._on_fsm_trying
        self._fsm.onafterlaunchercmd_up = self._on_fsm_launchercmd_up
        self._fsm.onafterdisconnect = self._on_fsm_disconnect
        self._fsm.onsyncing = self._on_fsm_syncing
        self._fsm.onafterlaunchercmd_trying = self._on_fsm_launchercmd_trying
        self._fsm.onafterlauncher_up = self._on_fsm_launcher_up
        self._fsm.onsynced = self._on_fsm_synced
        self._fsm.onafterlauncher_trying = self._on_fsm_launcher_trying
        self._fsm.onentersynced = self._on_fsm_synced_entry
        self._fsm.onleavesynced = self._on_fsm_synced_exit

    def _on_fsm_down(self, _):
        if self.debuglevel > 0:
            print('[%s]: state DOWN' % self.debugname)
        for cb in self.on_state_changed:
            cb('down')
        return True

    def _on_fsm_connect(self, _):
        if self.debuglevel > 0:
            print('[%s]: event CONNECT' % self.debugname)
        self.start_launchercmd_channel()
        return True

    def _on_fsm_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: state TRYING' % self.debugname)
        for cb in self.on_state_changed:
            cb('trying')
        return True

    def _on_fsm_launchercmd_up(self, _):
        if self.debuglevel > 0:
            print('[%s]: event LAUNCHERCMD UP' % self.debugname)
        self.start_launcher_channel()
        return True

    def _on_fsm_disconnect(self, _):
        if self.debuglevel > 0:
            print('[%s]: event DISCONNECT' % self.debugname)
        self.stop_launchercmd_channel()
        self.stop_launcher_channel()
        return True

    def _on_fsm_syncing(self, _):
        if self.debuglevel > 0:
            print('[%s]: state SYNCING' % self.debugname)
        for cb in self.on_state_changed:
            cb('syncing')
        return True

    def _on_fsm_launchercmd_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: event LAUNCHERCMD TRYING' % self.debugname)
        self.stop_launcher_channel()
        return True

    def _on_fsm_launcher_up(self, _):
        if self.debuglevel > 0:
            print('[%s]: event LAUNCHER UP' % self.debugname)
        return True

    def _on_fsm_synced(self, _):
        if self.debuglevel > 0:
            print('[%s]: state SYNCED' % self.debugname)
        for cb in self.on_state_changed:
            cb('synced')
        return True

    def _on_fsm_launcher_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: event LAUNCHER TRYING' % self.debugname)
        return True

    def _on_fsm_synced_entry(self, _):
        if self.debuglevel > 0:
            print('[%s]: state SYNCED entry' % self.debugname)
        self.sync_status()
        return True

    def _on_fsm_synced_exit(self, _):
        if self.debuglevel > 0:
            print('[%s]: state SYNCED exit' % self.debugname)
        self.unsync_status()
        return True

    @property
    def error_string(self):
        return self._error_string

    @error_string.setter
    def error_string(self, string):
        if self._error_string is string:
            return
        self._error_string = string
        for cb in self.on_error_string_changed:
            cb(string)

    @property
    def launchercmd_uri(self):
        return self._launchercmd_channel.socket_uri

    @launchercmd_uri.setter
    def launchercmd_uri(self, value):
        self._launchercmd_channel.socket_uri = value

    @property
    def launcher_uri(self):
        return self._launcher_channel.socket_uri

    @launcher_uri.setter
    def launcher_uri(self, value):
        self._launcher_channel.socket_uri = value

    def sync_status(self):
        print('WARNING: slot sync status unimplemented')

    def unsync_status(self):
        print('WARNING: slot unsync status unimplemented')

    def start(self):
        if self._fsm.isstate('down'):
            self._fsm.connect()

    def stop(self):
        if self._fsm.isstate('trying'):
            self._fsm.disconnect()
        elif self._fsm.isstate('syncing'):
            self._fsm.disconnect()
        elif self._fsm.isstate('synced'):
            self._fsm.disconnect()

    def add_launcher_topic(self, name):
        self._launcher_channel.add_socket_topic(name)

    def remove_launcher_topic(self, name):
        self._launcher_channel.remove_socket_topic(name)

    def clear_launcher_topics(self):
        self._launcher_channel.clear_socket_topics()

    def start_launchercmd_channel(self):
        self._launchercmd_channel.start()

    def stop_launchercmd_channel(self):
        self._launchercmd_channel.stop()

    def start_launcher_channel(self):
        self._launcher_channel.start()

    def stop_launcher_channel(self):
        self._launcher_channel.stop()

    # process all messages received on launchercmd
    def _launchercmd_channel_message_received(self, rx):

        # react to error message
        if rx.type == pb.MT_ERROR:
            # update error string with note
            self.error_string = ''
            for note in rx.note:
                self.error_string += note + '\n'

        for cb in self.on_launchercmd_message_received:
            cb(rx)

    # process all messages received on launcher
    def _launcher_channel_message_received(self, identity, rx):

        # react to launcher full update message
        if rx.type == pb.MT_LAUNCHER_FULL_UPDATE:
            self.launcher_full_update_received(identity, rx)

        # react to launcher incremental update message
        elif rx.type == pb.MT_LAUNCHER_INCREMENTAL_UPDATE:
            self.launcher_incremental_update_received(identity, rx)

        for cb in self.on_launcher_message_received:
            cb(identity, rx)

    def launcher_full_update_received(self, identity, rx):
        print('SLOT launcher full update unimplemented')

    def launcher_incremental_update_received(self, identity, rx):
        print('SLOT launcher incremental update unimplemented')

    def send_launchercmd_message(self, msg_type, tx):
        self._launchercmd_channel.send_socket_message(msg_type, tx)

    def send_launcher_start(self, tx):
        self.send_launchercmd_message(pb.MT_LAUNCHER_START, tx)

    def send_launcher_kill(self, tx):
        self.send_launchercmd_message(pb.MT_LAUNCHER_KILL, tx)

    def send_launcher_terminate(self, tx):
        self.send_launchercmd_message(pb.MT_LAUNCHER_TERMINATE, tx)

    def send_launcher_write_stdin(self, tx):
        self.send_launchercmd_message(pb.MT_LAUNCHER_WRITE_STDIN, tx)

    def send_launcher_call(self, tx):
        self.send_launchercmd_message(pb.MT_LAUNCHER_CALL, tx)

    def send_launcher_shutdown(self, tx):
        self.send_launchercmd_message(pb.MT_LAUNCHER_SHUTDOWN, tx)

    def send_launcher_set(self, tx):
        self.send_launchercmd_message(pb.MT_LAUNCHER_SET, tx)

    def _launchercmd_channel_state_changed(self, state):

        if (state == 'trying'):
            if self._fsm.isstate('syncing'):
                self._fsm.launchercmd_trying()
            elif self._fsm.isstate('synced'):
                self._fsm.launchercmd_trying()

        elif (state == 'up'):
            if self._fsm.isstate('trying'):
                self._fsm.launchercmd_up()

    def _launcher_channel_state_changed(self, state):

        if (state == 'trying'):
            if self._fsm.isstate('synced'):
                self._fsm.launcher_trying()

        elif (state == 'up'):
            if self._fsm.isstate('syncing'):
                self._fsm.launcher_up()
