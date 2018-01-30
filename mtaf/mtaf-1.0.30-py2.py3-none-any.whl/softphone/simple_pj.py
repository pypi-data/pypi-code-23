from mtaf import mtaf_logging
from mtaf.trace import Trace
from mtaf.user_exception import UserException as Ux, UserTimeoutException as Tx
from mtaf.wav_audio import create_wav_file
import re
import threading
import random
import pjsua as pj
from time import time, sleep
import os
import struct

log = mtaf_logging.get_logger('mtaf.simple_pj')
# set console log level
mtaf_logging.console_handler.setLevel(mtaf_logging.INFO)
wav_dir = 'wav'

account_infos = {}

media_state_text = {
    pj.MediaState.NULL: 'NULL',
    pj.MediaState.ACTIVE: 'ACTIVE',
    pj.MediaState.LOCAL_HOLD: 'LOCAL HOLD',
    pj.MediaState.REMOTE_HOLD: 'REMOTE HOLD',
    pj.MediaState.ERROR: 'ERROR'
}

call_state_text = {
    pj.CallState.NULL: "NULL",
    pj.CallState.CALLING: "CALLING",
    pj.CallState.INCOMING: "INCOMING",
    pj.CallState.EARLY: "EARLY",
    pj.CallState.CONNECTING: "CONNECTING",
    pj.CallState.CONFIRMED: "CONFIRMED",
    pj.CallState.DISCONNECTED: "DISCONNECTED"
}


# callback to be used by the pjsip/pjsua C libraries formtaf_logging
def pjl_log_cb(level, _str, _len):
    sip_match = re.match('.*(Request|Response)', _str)
    lines = ["log_cb(%d): %s" % (level, line) for line in _str.splitlines()]
    if level == 1:
        for line in lines:
            log.warn(line)
    elif level == 2:
        for line in lines:
            log.info(line)
    elif sip_match:
        log.trace(lines[0])
        for line in lines:
            log.debug(line)
    else:
        for line in lines:
            log.debug(line)


# make this global to see if end-of-execution shutdown works better
# (previously it was a SoftphoneManager class attribute)


class SoftphoneManager:

    def __init__(self):
        self.softphones = {}

    def get_softphone(self, uri, proxy, password, null_snd, dns_list, tcp, reg_wait=True):
        if uri in self.softphones:
            self.softphones[uri].account_info.account.set_registration(True)
            log.debug("SoftphoneManager.get_softphone returning existing softphone %s" % uri)
        else:
            log.debug("SoftphoneManager.get_softphone creating softphone %s" % uri)
            self.softphones[uri] = Softphone(uri, proxy=proxy, password=password, null_snd=null_snd, dns_list=dns_list,
                                             tcp=tcp, reg_wait=False)
        if reg_wait:
            self.softphones[uri].account_info.account_cb.wait()
        return self.softphones[uri]

    def end_all_calls(self):
        for uri in self.softphones.keys():
            self.softphones[uri].end_call()

    def set_defaults(self):
        for uri in self.softphones.keys():
            self.softphones[uri].set_incoming_response(180)


class Softphone:

    lib = None
    dst_uri = None
    rec_id = None
    last_msg_length = 0

    @Trace(log)
    def __init__(self, uri, proxy, password, null_snd=True, dns_list=None, tcp=False,
                 pbfile='default', record=True, quiet=True, reg_wait=True):
        self.uri = uri
        # create and start the pjsua lib instance if not already started
        if not self.lib:
            Softphone.lib = PjsuaLib()
            self.lib.start(null_snd=null_snd, dns_list=dns_list, tcp=tcp)
        # add this account and start it registering
        m = re.match('sip:([^@]+)@(.+)', self.uri)
        if m:
            self.number = m.group(1)
            self.domain = m.group(2)
            self.account_info = self.lib.add_account(self.number, self.domain, proxy, password)
            if pbfile is None:
                self.account_info.pbfile_relpath = None
            else:
                if pbfile == 'default':
                    pbfile = '%s.wav' % ''.join(re.findall('\d', self.number))
                self.account_info.pbfile_relpath = os.path.join(wav_dir, pbfile)
                create_wav_file(self.account_info.pbfile_relpath, quiet)
            if reg_wait:
                self.account_info.account_cb.wait()
            self.account_info.record = record
            self.account_info.lib = self.lib

    # def __del__(self):
    #     if self.account_info.call:
    #         sleep(1)
    #         # log.debug("%s ending call to %s" % (self.uri, self.dst_uri))
    #         try:
    #             self.account_info.call.hangup()
    #             self.wait_for_call_status('idle')
    #         except TypeError:
    #             pass
    #     self.lib.delete_account(self.uri)

    @Trace(log)
    def wait_for_call_status(self, desired_status, timeout=20, warn_only=False):
        # possible desired_status values: 'call', 'idle', 'early', 'hold'
        start = time()
        while time() - start < timeout:
            log.debug("%s: call status is %s" % (self.uri, self.account_info.call_status))
            if self.account_info.call_status == desired_status:
                if self.account_info.call_status == 'idle':
                    self.account_info.call = None
                return time() - start
            sleep(0.1)
            if self.account_info.call_status == 'call' and desired_status == 'early':
                self.end_call()
                raise Ux('wait for call status "early" terminated call because status was "call"')
        else:
            if warn_only:
                log.warn('wait for call status "%s" timed out after %s seconds' % (desired_status, timeout))
            else:
                raise Tx('wait for call status "%s" timed out after %s seconds' % (desired_status, timeout))

    @Trace(log)
    def make_call_to_softphone(self, dst_uri, dst_response=None):
        self.dst_uri = dst_uri
        account_infos[dst_uri].incoming_response = dst_response
        if self.account_info.reg_status != 200:
            raise Ux("Can't set up call, registration status (src) %s" % self.account_info.reg_status)
        log.debug("%s calling %s" % (self.uri, self.dst_uri))
        self.account_info.call = self.account_info.account.make_call(self.dst_uri)
        self.account_info.call.set_callback(MyCallCallback(self.account_info))

    @Trace(log)
    def make_call(self, dst_uri):
        if self.account_info.reg_status != 200:
            raise Ux("Can't set up call, registration status (src) %s" % self.account_info.reg_status)
        log.debug("%s calling %s" % (self.uri, dst_uri))
        self.account_info.call = self.account_info.account.make_call(dst_uri)
        self.account_info.call.set_callback(MyCallCallback(self.account_info))

    @Trace(log)
    def end_call(self, timeout=10):
        if self.account_info.call is None:
            return
        log.debug("%s ending call to %s" % (self.uri, self.account_info.remote_uri))
        # sleep(5)
        if self.account_info.call is not None:
            try:
                # ignore any errors
                self.account_info.call.hangup()
                self.wait_for_call_status('idle', timeout)
            except:
                pass

    @Trace(log)
    def hold(self, timeout=10):
        if not self.account_info.call:
            raise Ux("hold(): %s not in call" % self.uri)
        log.debug("%s putting call to %s on hold" % (self.uri, self.account_info.remote_uri))
        self.account_info.call.hold()
        self.wait_for_call_status('hold', timeout)

    @Trace(log)
    def unhold(self, timeout=10):
        if not self.account_info.call:
            raise Ux("unhold(): %s not in call" % self.uri)
        log.debug("%s unholding call to %s" % (self.uri, self.account_info.remote_uri))
        self.account_info.call.unhold()
        self.wait_for_call_status('call', timeout)

    @Trace(log)
    def set_incoming_response(self, code):
        self.account_info.incoming_response = code

    @Trace(log)
    def send_response_code(self, code):
        if not self.account_info.call:
            raise Ux("send_response_code(): %s not in call" % self.uri)
        self.account_info.call.answer(code)

    @Trace(log)
    def leave_msg(self, length=None):
        if not self.account_info.call:
            raise Ux("leave_msg(): %s not in call" % self.uri)
        # wait 5 seconds so voice prompt will accept '2' key to accelerate to next prompt
        sleep(5)
        self.account_info.call.dial_dtmf('2')
        # wait 5 seconds to get past second prompt "leave a msg after the tone (beep)'
        sleep(5)
        if length is None:
            random.seed(time())
            for tries in range(20):
                length = random.randrange(10, 30, 1)
                if abs(length - self.last_msg_length) > 5:
                    self.last_msg_length = length
                    break
            else:
                raise Ux("couldn't get message length > 5 sec different from last msg")
        sleep(length)

    @Trace(log)
    def dial_dtmf(self, dtmf_string):
        if self.account_info.call:
            for c in list(dtmf_string):
                log.debug('%s:send dtmf %s' % (self.uri, c))
                self.account_info.call.dial_dtmf(c)
                sleep(0.3)

    @Trace(log)
    def set_monitor_on(self):
        pass

    @Trace(log)
    def set_monitor_off(self):
        pass

    @Trace(log)
    def unregister(self):
        self.account_info.account.set_registration(False)


class MyAccountCallback(pj.AccountCallback):

    sem = None
    call_info = None

    def __init__(self, account_info):
        pj.AccountCallback.__init__(self)
        log.debug("MyAccountCallback.__init__(%s)" % account_info)
        self.account_info = account_info
        pass

    def wait(self):
        self.sem = threading.Semaphore(0)
        log.debug("%s: acquiring semaphore")
        self.sem.acquire()

    def on_reg_state(self):
        reg_info = self.account.info()
        log.debug("%s: on_reg_state - registration status = %s (%s)" % (reg_info.uri, reg_info.reg_status,
                                                                        reg_info.reg_reason))
        self.account_info.reg_status = reg_info.reg_status
        if self.sem and self.account_info.reg_status == 200:
            self.sem.release()
            self.sem = None

    def on_incoming_call(self, call):
        log.debug('on_incoming_call: account_info = %s' % self.account_info)
        self.account_info.call = call
        call.set_callback(MyCallCallback(self.account_info))
        # on_incoming_call_cb defaults to None, but it can designate an external callback to be called here
        if self.account_info.incoming_response:
            call.answer(self.account_info.incoming_response)


# look up new_call_states[old_state][(call_state, media_state)]
# to get a dictionary that will contain 'new_state' and might contain 'media actions'
new_call_settings = {
    'idle': {
        (pj.CallState.CONFIRMED, pj.MediaState.ACTIVE): {'status': 'call', 'actions': [ 'create_media', 'connect_media']},
        (pj.CallState.EARLY, pj.MediaState.ACTIVE): {'status': 'early'},
        (pj.CallState.EARLY, pj.MediaState.NULL): {'status': 'early'},
        (pj.CallState.DISCONNECTED, pj.MediaState.ACTIVE): {'status': 'idle'},
        (pj.CallState.DISCONNECTED, pj.MediaState.NULL): {'status': 'idle'}
    },
    'early': {
        (pj.CallState.CONFIRMED, pj.MediaState.ACTIVE): {'status': 'call', 'actions': ['create_media', 'connect_media']},
        (pj.CallState.EARLY, pj.MediaState.ACTIVE): {'status': 'early'},
        (pj.CallState.EARLY, pj.MediaState.NULL): {'status': 'early'},
        (pj.CallState.DISCONNECTED, pj.MediaState.ACTIVE): {'status': 'idle', 'actions': ['delete_call']},
        (pj.CallState.DISCONNECTED, pj.MediaState.NULL): {'status': 'idle', 'actions': ['delete_call']}
    },
    'call': {
        (pj.CallState.CONFIRMED, pj.MediaState.ACTIVE): {'status': 'call', 'actions': ['connect_media']},
        (pj.CallState.CONFIRMED, pj.MediaState.NULL): {'status': 'hold'},
        (pj.CallState.DISCONNECTED, pj.MediaState.ACTIVE): {'status': 'idle', 'actions': ['destroy_media', 'delete_call']},
        (pj.CallState.DISCONNECTED, pj.MediaState.NULL): {'status': 'idle', 'actions': ['destroy_media', 'delete_call']}
    },
    'hold': {
        (pj.CallState.CONFIRMED, pj.MediaState.ACTIVE): {'status': 'call', 'actions': ['connect_media']},
        (pj.CallState.CONFIRMED, pj.MediaState.NULL): {'status': 'hold'},
        (pj.CallState.DISCONNECTED, pj.MediaState.ACTIVE): {'status': 'idle', 'actions': ['destroy_media', 'delete_call']},
        (pj.CallState.DISCONNECTED, pj.MediaState.NULL): {'status': 'idle', 'actions': ['destroy_media', 'delete_call']}
    },
}


class MyCallCallback(pj.CallCallback):
    """Callback to receive events from Call"""
    def __init__(self, account_info):
        pj.CallCallback.__init__(self, account_info.call)
        self.account_info = account_info
        self.rec_id = None
        self.pb_id = None
        self.pb_slot = None
        self.account_info.state = pj.CallState.NULL
        self.media_connected = False
        self.media_call_slot = None

    def _on_state(self):
        media_ops = {
            'create_media': self.create_media,
            'connect_media': self.connect_media,
            'destroy_media': self.destroy_media,
            'delete_call': self.delete_call
        }
        call_info = self.account_info.call.info()
        remote_uri = re.match('("[^"]*"\s+)?<?([^>]+)', call_info.remote_uri).group(2)
        self.account_info.state = call_info.state
        self.account_info.media_state = call_info.media_state
        log.debug("_on_state: %s: ci.remote_uri=%s state %s media_state %s" % (
            call_info.uri, remote_uri, call_state_text[call_info.state], media_state_text[call_info.media_state]))
        old_call_status = self.account_info.call_status
        state_key = (call_info.state, call_info.media_state)
        if state_key in new_call_settings[old_call_status]:
            new_call_status = new_call_settings[old_call_status][state_key]['status']
            if 'actions' in new_call_settings[old_call_status][state_key]:
                actions = new_call_settings[old_call_status][state_key]['actions']
            else:
                actions = {}
        else:
            new_call_status = self.account_info.call_status
            actions = {}
        log.debug("_on_state: old call_status = %s, new call_status = %s" % (old_call_status, new_call_status))
        if new_call_status == 'call' and old_call_status != 'call':
            self.account_info.call_start_time = time()
        self.account_info.call_status = new_call_status
        if self.account_info.call_status == 'idle':
            self.account_info.remote_uri = None
        else:
            self.account_info.remote_uri = remote_uri
        for action in actions:
            media_ops[action]()

    def on_state(self):
        with mtaf_logging.msg_src_cm('on_state'):
            self._on_state()

    def on_media_state(self):
        with mtaf_logging.msg_src_cm('on_media_state'):
            self._on_state()

    @Trace(log)
    def create_media(self):
        if self.pb_id is not None:
            raise Ux('create_media: player already exists')
        if self.rec_id is not None:
            raise Ux('create_media: recorder already exists')
        if self.media_call_slot is not None:
            raise Ux('create_media: self.media_call_slot should be None')
        uri = self.account_info.uri
        pbfile_relpath = self.account_info.pbfile_relpath
        lib = self.account_info.lib
        record = self.account_info.record
        if pbfile_relpath is None:
            log.debug("%s: pbfile_relpath not defined, no player created" % uri)
        else:
            log.debug("%s: creating player with pbfile_relpath = %s" % (uri, pbfile_relpath))
            self.pb_id = lib.create_player(pbfile_relpath, loop=True)
            self.pb_slot = lib.player_get_slot(self.pb_id)
            log.debug("%s: created player %s at slot %d" % (uri, self.pb_id, self.pb_slot))
        if record:
            rec_file = os.path.join(wav_dir, "rec_%s.wav" % self.account_info.number)
            log.debug("%s: rec file = %s" % (uri, rec_file))
            self.rec_id = lib.create_recorder(rec_file)
            rec_slot = lib.recorder_get_slot(self.rec_id)
            log.debug("%s: created recorder %s at slot %d" % (uri, self.rec_id, rec_slot))

    @Trace(log)
    def destroy_media(self):
        uri = self.account_info.uri
        lib = self.account_info.lib
        if self.pb_id is None and self.rec_id is None:
            if self.media_call_slot is not None:
                raise Ux('destroy_media: self.media_call_slot is not None, media should be disconnected first')
            log.debug('destroy_media: no media have been created')
            return
        if self.pb_id is None:
            log.debug("%s: self.pb_id is None, no player destroyed" % uri)
        else:
            log.debug("%s: destroying player" % uri)
            lib.player_destroy(self. pb_id)
            self.pb_id = None
        if self.rec_id is None:
            log.debug("%s: self.rec_id is None, no recorder destroyed" % uri)
        else:
            lib.recorder_destroy(self.rec_id)
            self.rec_id = None
            # rec_file = os.path.join(wav_dir, "rec_%s.wav" % self.account_info.number)
            # self.patch_recfile(rec_file)

    @Trace(log)
    def patch_recfile(self, rec_file):
        # patch the wav file by adding size fields so wave module won't reject file
        #    (pjsip is supposed to do this when recorder is destroyed, but doesn't)
        with open(rec_file, 'r+b') as f:
            flen = len(f.read())
            f.seek(4)
            f.write(struct.pack('I', flen - 8))
            f.seek(40)
            f.write(struct.pack('I', flen - 44))

    @Trace(log)
    def delete_call(self):
        log.debug("%s: called delete_call" % self.account_info.uri)
        self.account_info.call = None
        self.account_info.call_status = 'idle'

    @Trace(log)
    def connect_media(self):
        if self.rec_id is None:
            raise Ux("connect_media: no recorder exists, not connecting")
        if self.pb_id is None:
            log.debug('%s: connect_media: no player exists, not connecting')
        if self.rec_id is None and self.pb_id is None:
            return
        lib = self.account_info.lib
        uri = self.account_info.uri
        rec_slot = lib.recorder_get_slot(self.rec_id)
        conf_slot = self.account_info.call.info().conf_slot
        # self.media_call_slot is set to the call's conference slot when connecting media,
        # and set to None when disconnecting, so if it is not None, this is a reconnect
        if self.media_call_slot is not None:
            # disconnect, then reconnect to the same slot
            if self.rec_id is not None:
                log.debug("%s: disconnecting call slot %d from recorder %s at slot %d"
                          % (uri, self.media_call_slot, self.rec_id, rec_slot))
                lib.conf_disconnect(self.media_call_slot, rec_slot)
            if self.pb_id is not None:
                self.pb_slot = lib.player_get_slot(self.pb_id)
                log.debug("%s: disconnecting player %s at slot %d to call slot %d"
                          % (uri, self.pb_id, self.pb_slot, self.media_call_slot))
                lib.conf_disconnect(self.pb_slot, self.media_call_slot)
        if self.rec_id is not None:
            log.debug("%s: connecting call slot %d to recorder %s at slot %d"
                      % (uri, conf_slot, self.rec_id, rec_slot))
            lib.conf_connect(conf_slot, rec_slot)
        if self.pb_id is not None:
            self.pb_slot = lib.player_get_slot(self.pb_id)
            log.debug("%s: connecting player %s at slot %d to call slot %d"
                      % (uri, self.pb_id, self.pb_slot, conf_slot))
            lib.conf_connect(self.pb_slot, conf_slot)
        self.media_call_slot = conf_slot

    # maybe this will be needed at some point but it's not necessary when call_status goes from 'call' to 'hold';
    # call.hold() disconnects the media as a side effect, but it needs to be reconnected explicitly using connect_media
    # when call.unhold() causes the call_status to change from 'hold' back to 'call'
    #
    # @Trace(log)
    # def disconnect_media(self):
    #     if self.rec_id is None:
    #         raise Ux("disconnect_media: no recorder exists, not disconnecting")
    #     if self.pb_id is None:
    #         log.debug('%s: disconnect_media: no player exists, not disconnecting')
    #     if self.rec_id is None and self.pb_id is None:
    #         return
    #     if self.media_call_slot is None:
    #         raise Ux('disconnect_media: media not connected')
    #     lib = self.account_info.lib
    #     uri = self.account_info.uri
    #     conf_slot = self.account_info.call.info().conf_slot
    #     if self.media_call_slot != conf_slot:
    #         raise Ux('disconnect_media: self.media_call_slot (%s) not equal to conf_slot (%s)' % (
    #             self.media_call_slot, conf_slot))
    #     if self.rec_id is not None:
    #         rec_slot = lib.recorder_get_slot(self.rec_id)
    #         log.debug("%s: disconnecting call slot %d from recorder %s at slot %d"
    #                   % (uri, self.media_call_slot, self.rec_id, rec_slot))
    #         lib.conf_disconnect(self.media_call_slot, rec_slot)
    #     if self.pb_id is not None:
    #         self.pb_slot = lib.player_get_slot(self.pb_id)
    #         log.debug("%s: disconnecting player %s at slot %d to call slot %d"
    #                   % (uri, self.pb_id, self.pb_slot, self.media_call_slot))
    #         lib.conf_disconnect(self.pb_slot, self.media_call_slot)
    #     self.media_call_slot = None


class MyAccountInfo:

    def __init__(self, account, uri, number):
        self.account = account
        self.uri = uri
        self.number = number
        self.state = pj.CallState.NULL
        self.media_state = pj.MediaState.NULL
        self.call_status = 'idle'
        self.reg_status = None
        self.call = None
        self.hold = False
        self.incoming_response = None
        self.remote_uri = None
        self.call_start_time = None


class PjsuaLib(pj.Lib):

    def __init__(self, quality=10, tx_drop_pct=0, rx_drop_pct=0, no_vad=True):
        pj.Lib.__init__(self)
        self.quality = quality
        self.tx_drop_pct = tx_drop_pct
        self.rx_drop_pct = rx_drop_pct
        self.tcp = False
        self.no_vad = no_vad

    def start(self, log_cb=pjl_log_cb, null_snd=False, tcp=False, dns_list=None):
        self.tcp = tcp
        my_ua_cfg = pj.UAConfig()
        my_media_cfg = pj.MediaConfig()

        # set these maximum values to accommodate the number of softphones that will be created;
        # a call from one softphone to another requires 4 distinct call IDs and uses 6 media slots
        my_ua_cfg.max_calls = 200
        my_media_cfg.max_media_ports = 302

        my_media_cfg.tx_drop_pct = self.tx_drop_pct
        my_media_cfg.rx_drop_pct = self.rx_drop_pct
        my_media_cfg.quality = self.quality
        my_media_cfg.ptime = 20
        my_media_cfg.no_vad = self.no_vad
        if dns_list:
            my_ua_cfg.nameserver = dns_list
        self.init(log_cfg=pj.LogConfig(level=4, callback=log_cb), ua_cfg=my_ua_cfg, media_cfg=my_media_cfg)
        if self.tcp:
            transport = self.create_transport(pj.TransportType.TCP, pj.TransportConfig())
        else:
            transport = self.create_transport(pj.TransportType.UDP, pj.TransportConfig())
        log.debug("Listening on %s:%s" % (transport.info().host, transport.info().port))
        pj.Lib.start(self)
        if null_snd:
            self.set_null_snd_dev()
        self.set_codec_priority('PCMU/8000/1', 150)
        self.set_codec_priority('PCMU/8000/1', 149)
        self.set_codec_priority('G722/16000/1', 148)

    @Trace(log)
    def add_account(self, number, domain, proxy, pw):
        uri = "sip:%s@%s" % (number, domain)
        if uri in account_infos:
            log.debug('%s: [add_account] using existing account' % uri)
            return account_infos[uri]
        log.debug('%s: [add_account] creating account' % uri)
        acc_cfg = pj.AccountConfig()
        acc_cfg.id = uri
        acc_cfg.reg_uri = "sip:%s" % proxy
        acc_cfg.proxy = ["sip:%s" % proxy]
        acc_cfg.allow_contact_rewrite = False
        acc_cfg.auth_cred = [pj.AuthCred(realm="*", username=number, passwd=pw)]
        account = self.create_account(acc_cfg)
        account_info = MyAccountInfo(account, uri, number)
        account_info.account_cb = MyAccountCallback(account_info)
        account.set_callback(account_info.account_cb)
        account_infos[uri] = account_info
        return account_info

    @staticmethod
    @Trace(log)
    def delete_account(uri):
        log.debug('%s: [delete_account] deleting existing account' % uri)
        account_infos[uri].account.delete()
        del account_infos[uri]

