import zmq
import threading
import uuid
from fysom import Fysom
from ..common.rpcclient import RpcClient
from ..common.subscribe import Subscribe
from ..common.publish import Publish

import machinetalk.protobuf.types_pb2 as pb
from machinetalk.protobuf.message_pb2 import Container


class SyncClient(object):
    def __init__(self, debuglevel=0, debugname='Sync Client'):
        self.debuglevel = debuglevel
        self.debugname = debugname
        self._error_string = ''
        self.on_error_string_changed = []

        # Sync
        self._sync_channel = RpcClient(debuglevel=debuglevel)
        self._sync_channel.debugname = '%s - %s' % (self.debugname, 'sync')
        self._sync_channel.on_state_changed.append(self._sync_channel_state_changed)
        self._sync_channel.on_socket_message_received.append(self._sync_channel_message_received)
        # more efficient to reuse protobuf messages
        self._sync_rx = Container()
        self._sync_tx = Container()

        # Sub
        self._sub_channel = Subscribe(debuglevel=debuglevel)
        self._sub_channel.debugname = '%s - %s' % (self.debugname, 'sub')
        self._sub_channel.on_state_changed.append(self._sub_channel_state_changed)
        self._sub_channel.on_socket_message_received.append(self._sub_channel_message_received)
        # more efficient to reuse protobuf messages
        self._sub_rx = Container()

        # Pub
        self._pub_channel = Publish(debuglevel=debuglevel)
        self._pub_channel.debugname = '%s - %s' % (self.debugname, 'pub')
        # more efficient to reuse protobuf messages
        self._pub_tx = Container()

        # callbacks
        self.on_sync_message_received = []
        self.on_sub_message_received = []
        self.on_state_changed = []

        # fsm
        self._fsm = Fysom({'initial': 'down',
                          'events': [
                            {'name': 'start', 'src': 'down', 'dst': 'trying'},
                            {'name': 'sync_state_up', 'src': 'trying', 'dst': 'syncing'},
                            {'name': 'stop', 'src': 'trying', 'dst': 'down'},
                            {'name': 'sync_state_trying', 'src': 'syncing', 'dst': 'trying'},
                            {'name': 'sub_state_up', 'src': 'syncing', 'dst': 'synced'},
                            {'name': 'stop', 'src': 'syncing', 'dst': 'down'},
                            {'name': 'sub_state_trying', 'src': 'synced', 'dst': 'syncing'},
                            {'name': 'sync_state_trying', 'src': 'synced', 'dst': 'trying'},
                            {'name': 'stop', 'src': 'synced', 'dst': 'down'},
                          ]})

        self._fsm.ondown = self._on_fsm_down
        self._fsm.onafterstart = self._on_fsm_start
        self._fsm.ontrying = self._on_fsm_trying
        self._fsm.onaftersync_state_up = self._on_fsm_sync_state_up
        self._fsm.onafterstop = self._on_fsm_stop
        self._fsm.onsyncing = self._on_fsm_syncing
        self._fsm.onaftersync_state_trying = self._on_fsm_sync_state_trying
        self._fsm.onaftersub_state_up = self._on_fsm_sub_state_up
        self._fsm.onsynced = self._on_fsm_synced
        self._fsm.onaftersub_state_trying = self._on_fsm_sub_state_trying

    def _on_fsm_down(self, _):
        if self.debuglevel > 0:
            print('[%s]: state DOWN' % self.debugname)
        for cb in self.on_state_changed:
            cb('down')
        return True

    def _on_fsm_start(self, _):
        if self.debuglevel > 0:
            print('[%s]: event START' % self.debugname)
        self.start_sync_channel()
        self.start_pub_channel()
        return True

    def _on_fsm_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: state TRYING' % self.debugname)
        for cb in self.on_state_changed:
            cb('trying')
        return True

    def _on_fsm_sync_state_up(self, _):
        if self.debuglevel > 0:
            print('[%s]: event SYNC STATE UP' % self.debugname)
        self.send_sync()
        self.start_sub_channel()
        return True

    def _on_fsm_stop(self, _):
        if self.debuglevel > 0:
            print('[%s]: event STOP' % self.debugname)
        self.stop_sync_channel()
        self.stop_sub_channel()
        self.stop_pub_channel()
        return True

    def _on_fsm_syncing(self, _):
        if self.debuglevel > 0:
            print('[%s]: state SYNCING' % self.debugname)
        for cb in self.on_state_changed:
            cb('syncing')
        return True

    def _on_fsm_sync_state_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: event SYNC STATE TRYING' % self.debugname)
        self.stop_sub_channel()
        return True

    def _on_fsm_sub_state_up(self, _):
        if self.debuglevel > 0:
            print('[%s]: event SUB STATE UP' % self.debugname)
        self.synced()
        return True

    def _on_fsm_synced(self, _):
        if self.debuglevel > 0:
            print('[%s]: state SYNCED' % self.debugname)
        for cb in self.on_state_changed:
            cb('synced')
        return True

    def _on_fsm_sub_state_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: event SUB STATE TRYING' % self.debugname)
        self.send_sync()
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
    def sync_uri(self):
        return self._sync_channel.socket_uri

    @sync_uri.setter
    def sync_uri(self, value):
        self._sync_channel.socket_uri = value

    @property
    def sub_uri(self):
        return self._sub_channel.socket_uri

    @sub_uri.setter
    def sub_uri(self, value):
        self._sub_channel.socket_uri = value

    @property
    def pub_uri(self):
        return self._pub_channel.socket_uri

    @pub_uri.setter
    def pub_uri(self, value):
        self._pub_channel.socket_uri = value

    @property
    def pub_port(self):
        return self._pub_channel.socket_port

    @property
    def pub_dsn(self):
        return self._pub_channel.socket_dsn

    def start(self):
        if self._fsm.isstate('down'):
            self._fsm.start()

    def stop(self):
        if self._fsm.isstate('trying'):
            self._fsm.stop()
        elif self._fsm.isstate('syncing'):
            self._fsm.stop()
        elif self._fsm.isstate('synced'):
            self._fsm.stop()

    def add_sub_topic(self, name):
        self._sub_channel.add_socket_topic(name)

    def remove_sub_topic(self, name):
        self._sub_channel.remove_socket_topic(name)

    def clear_sub_topics(self):
        self._sub_channel.clear_socket_topics()

    def add_pub_topic(self, name):
        self._pub_channel.add_socket_topic(name)

    def remove_pub_topic(self, name):
        self._pub_channel.remove_socket_topic(name)

    def clear_pub_topics(self):
        self._pub_channel.clear_socket_topics()

    def start_sync_channel(self):
        self._sync_channel.start()

    def stop_sync_channel(self):
        self._sync_channel.stop()

    def start_sub_channel(self):
        self._sub_channel.start()

    def stop_sub_channel(self):
        self._sub_channel.stop()

    def start_pub_channel(self):
        self._pub_channel.start()

    def stop_pub_channel(self):
        self._pub_channel.stop()

    # process all messages received on sync
    def _sync_channel_message_received(self, rx):

        for cb in self.on_sync_message_received:
            cb(rx)

    # process all messages received on sub
    def _sub_channel_message_received(self, identity, rx):

        for cb in self.on_sub_message_received:
            cb(identity, rx)

    def send_sync_message(self, msg_type, tx):
        self._sync_channel.send_socket_message(msg_type, tx)

    def send_pub_message(self, identity, msg_type, tx):
        self._pub_channel.send_socket_message(identity, msg_type, tx)

    def send_sync(self):
        tx = self._sync_tx
        self.send_sync_message(pb.MT_SYNC, tx)

    def send_incremental_update(self, identity, tx):
        ids = [identity]
        for receiver in ids:
            self.send_pub_message(receiver, pb.MT_INCREMENTAL_UPDATE, tx)

    def _sync_channel_state_changed(self, state):

        if (state == 'trying'):
            if self._fsm.isstate('syncing'):
                self._fsm.sync_state_trying()
            elif self._fsm.isstate('synced'):
                self._fsm.sync_state_trying()

        elif (state == 'up'):
            if self._fsm.isstate('trying'):
                self._fsm.sync_state_up()

    def _sub_channel_state_changed(self, state):

        if (state == 'trying'):
            if self._fsm.isstate('synced'):
                self._fsm.sub_state_trying()

        elif (state == 'up'):
            if self._fsm.isstate('syncing'):
                self._fsm.sub_state_up()
