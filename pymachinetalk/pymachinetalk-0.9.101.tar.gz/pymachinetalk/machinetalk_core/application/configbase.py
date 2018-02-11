import zmq
import threading
import uuid
from fysom import Fysom
from ..common.rpcclient import RpcClient

import machinetalk.protobuf.types_pb2 as pb
from machinetalk.protobuf.message_pb2 import Container


class ConfigBase(object):
    def __init__(self, debuglevel=0, debugname='Config Base'):
        self.debuglevel = debuglevel
        self.debugname = debugname
        self._error_string = ''
        self.on_error_string_changed = []

        # Config
        self._config_channel = RpcClient(debuglevel=debuglevel)
        self._config_channel.debugname = '%s - %s' % (self.debugname, 'config')
        self._config_channel.on_state_changed.append(self._config_channel_state_changed)
        self._config_channel.on_socket_message_received.append(self._config_channel_message_received)
        # more efficient to reuse protobuf messages
        self._config_rx = Container()
        self._config_tx = Container()

        # callbacks
        self.on_config_message_received = []
        self.on_state_changed = []

        # fsm
        self._fsm = Fysom({'initial': 'down',
                          'events': [
                            {'name': 'connect', 'src': 'down', 'dst': 'trying'},
                            {'name': 'config_up', 'src': 'trying', 'dst': 'listing'},
                            {'name': 'disconnect', 'src': 'trying', 'dst': 'down'},
                            {'name': 'application_retrieved', 'src': 'listing', 'dst': 'up'},
                            {'name': 'config_trying', 'src': 'listing', 'dst': 'trying'},
                            {'name': 'disconnect', 'src': 'listing', 'dst': 'down'},
                            {'name': 'config_trying', 'src': 'up', 'dst': 'trying'},
                            {'name': 'load_application', 'src': 'up', 'dst': 'loading'},
                            {'name': 'disconnect', 'src': 'up', 'dst': 'down'},
                            {'name': 'application_loaded', 'src': 'loading', 'dst': 'up'},
                            {'name': 'config_trying', 'src': 'loading', 'dst': 'trying'},
                            {'name': 'disconnect', 'src': 'loading', 'dst': 'down'},
                          ]})

        self._fsm.ondown = self._on_fsm_down
        self._fsm.onafterconnect = self._on_fsm_connect
        self._fsm.ontrying = self._on_fsm_trying
        self._fsm.onafterconfig_up = self._on_fsm_config_up
        self._fsm.onafterdisconnect = self._on_fsm_disconnect
        self._fsm.onlisting = self._on_fsm_listing
        self._fsm.onafterapplication_retrieved = self._on_fsm_application_retrieved
        self._fsm.onafterconfig_trying = self._on_fsm_config_trying
        self._fsm.onup = self._on_fsm_up
        self._fsm.onafterload_application = self._on_fsm_load_application
        self._fsm.onenterup = self._on_fsm_up_entry
        self._fsm.onleaveup = self._on_fsm_up_exit
        self._fsm.onloading = self._on_fsm_loading
        self._fsm.onafterapplication_loaded = self._on_fsm_application_loaded

    def _on_fsm_down(self, _):
        if self.debuglevel > 0:
            print('[%s]: state DOWN' % self.debugname)
        for cb in self.on_state_changed:
            cb('down')
        return True

    def _on_fsm_connect(self, _):
        if self.debuglevel > 0:
            print('[%s]: event CONNECT' % self.debugname)
        self.start_config_channel()
        return True

    def _on_fsm_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: state TRYING' % self.debugname)
        for cb in self.on_state_changed:
            cb('trying')
        return True

    def _on_fsm_config_up(self, _):
        if self.debuglevel > 0:
            print('[%s]: event CONFIG UP' % self.debugname)
        self.send_list_applications()
        return True

    def _on_fsm_disconnect(self, _):
        if self.debuglevel > 0:
            print('[%s]: event DISCONNECT' % self.debugname)
        self.stop_config_channel()
        return True

    def _on_fsm_listing(self, _):
        if self.debuglevel > 0:
            print('[%s]: state LISTING' % self.debugname)
        for cb in self.on_state_changed:
            cb('listing')
        return True

    def _on_fsm_application_retrieved(self, _):
        if self.debuglevel > 0:
            print('[%s]: event APPLICATION RETRIEVED' % self.debugname)
        return True

    def _on_fsm_config_trying(self, _):
        if self.debuglevel > 0:
            print('[%s]: event CONFIG TRYING' % self.debugname)
        return True

    def _on_fsm_up(self, _):
        if self.debuglevel > 0:
            print('[%s]: state UP' % self.debugname)
        for cb in self.on_state_changed:
            cb('up')
        return True

    def _on_fsm_load_application(self, _):
        if self.debuglevel > 0:
            print('[%s]: event LOAD APPLICATION' % self.debugname)
        return True

    def _on_fsm_up_entry(self, _):
        if self.debuglevel > 0:
            print('[%s]: state UP entry' % self.debugname)
        self.sync_config()
        return True

    def _on_fsm_up_exit(self, _):
        if self.debuglevel > 0:
            print('[%s]: state UP exit' % self.debugname)
        self.unsync_config()
        return True

    def _on_fsm_loading(self, _):
        if self.debuglevel > 0:
            print('[%s]: state LOADING' % self.debugname)
        for cb in self.on_state_changed:
            cb('loading')
        return True

    def _on_fsm_application_loaded(self, _):
        if self.debuglevel > 0:
            print('[%s]: event APPLICATION LOADED' % self.debugname)
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
    def config_uri(self):
        return self._config_channel.socket_uri

    @config_uri.setter
    def config_uri(self, value):
        self._config_channel.socket_uri = value

    def sync_config(self):
        print('WARNING: slot sync config unimplemented')

    def unsync_config(self):
        print('WARNING: slot unsync config unimplemented')

    def start(self):
        if self._fsm.isstate('down'):
            self._fsm.connect()

    def stop(self):
        if self._fsm.isstate('trying'):
            self._fsm.disconnect()
        elif self._fsm.isstate('listing'):
            self._fsm.disconnect()
        elif self._fsm.isstate('up'):
            self._fsm.disconnect()
        elif self._fsm.isstate('loading'):
            self._fsm.disconnect()

    def start_config_channel(self):
        self._config_channel.start()

    def stop_config_channel(self):
        self._config_channel.stop()

    # process all messages received on config
    def _config_channel_message_received(self, rx):

        # react to describe application message
        if rx.type == pb.MT_DESCRIBE_APPLICATION:
            if self._fsm.isstate('listing'):
                self._fsm.application_retrieved()
            self.describe_application_received(rx)

        # react to application detail message
        elif rx.type == pb.MT_APPLICATION_DETAIL:
            if self._fsm.isstate('loading'):
                self._fsm.application_loaded()
            self.application_detail_received(rx)

        # react to error message
        elif rx.type == pb.MT_ERROR:
            # update error string with note
            self.error_string = ''
            for note in rx.note:
                self.error_string += note + '\n'

        for cb in self.on_config_message_received:
            cb(rx)

    def describe_application_received(self, rx):
        print('SLOT describe application unimplemented')

    def application_detail_received(self, rx):
        print('SLOT application detail unimplemented')

    def send_config_message(self, msg_type, tx):
        self._config_channel.send_socket_message(msg_type, tx)

        if msg_type == pb.MT_RETRIEVE_APPLICATION:
            if self._fsm.isstate('up'):
                self._fsm.load_application()

    def send_list_applications(self):
        tx = self._config_tx
        self.send_config_message(pb.MT_LIST_APPLICATIONS, tx)

    def send_retrieve_application(self, tx):
        self.send_config_message(pb.MT_RETRIEVE_APPLICATION, tx)

    def _config_channel_state_changed(self, state):

        if (state == 'trying'):
            if self._fsm.isstate('listing'):
                self._fsm.config_trying()
            elif self._fsm.isstate('up'):
                self._fsm.config_trying()
            elif self._fsm.isstate('loading'):
                self._fsm.config_trying()

        elif (state == 'up'):
            if self._fsm.isstate('trying'):
                self._fsm.config_up()
