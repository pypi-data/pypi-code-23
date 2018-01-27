import struct
import subprocess
import threading
from time import sleep

from scapy.layers.dot11 import Dot11, Dot11Elt, sendp, Dot11Deauth, RadioTap
from termcolor import cprint

from pywiface.models import Station, AP
from pywiface.threads import ScannerThread


class WirelessInterface:
    def __init__(self, name: str, essid: str = None, monitor_mode: bool = False, channel=None):
        self.name = name
        self.monitor_mode = monitor_mode
        if monitor_mode:
            self.set_monitor_mode()
        self.stations = {}
        self.aps = {}
        self.lock = threading.Lock()
        self.channel_lock = threading.Lock()
        self.ap_sema = threading.Semaphore(0)
        self.sta_sema = threading.Semaphore(0)
        self.essid = essid
        self.bssid = None
        self.scan_thread = None
        self._channel = channel
        self.hop = True
        if channel:
            self.set_channel(channel)
            self.hop = False

    def set_up(self):
        subprocess.run(['/bin/ip', 'link', 'set', self.name, 'up'])

    def set_down(self):
        subprocess.run(['/bin/ip', 'link', 'set', self.name, 'down'])

    def set_monitor_mode(self):
        self.set_down()
        subprocess.run(['/sbin/iw', 'dev', self.name, 'set', 'monitor', 'none'])
        self.set_up()
        self.monitor_mode = True

    def set_managed_mode(self):
        self.set_down()
        subprocess.run(['/sbin/iw', 'dev', self.name, 'set', 'type', 'managed'])
        self.set_up()
        self.monitor_mode = False

    def get_frequency(self):
        return struct.pack("<h", 2407 + (self._channel * 5))

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self.set_channel(value)

    def set_channel(self, channel):
        # in USA reg domain
        if 1 <= channel <= 11:
            subprocess.run(['/sbin/iw', 'dev', self.name, 'set', 'channel', str(channel)])
        self._channel = channel

    def set_mac(self, mac):
        self.set_down()
        subprocess.run(['/bin/ip', 'link', 'set', 'dev', self.name, 'address', mac], stdout=subprocess.DEVNULL)
        self.set_up()

    def reset_mac(self):
        self.set_down()
        subprocess.run(['/usr/bin/macchanger', '-p', self.name], stdout=subprocess.DEVNULL)
        self.set_up()

    def spoof_mac(self):
        self.set_down()
        subprocess.run(['/usr/bin/macchanger', '-A', self.name], stdout=subprocess.DEVNULL)
        self.set_up()


class MonitorInterface(WirelessInterface):
    def __init__(self, name: str, channel=None):
        super().__init__(name, monitor_mode=True, channel=channel)

    def deauth(self, target_mac: str, source_mac: str, count=1, burst_count=200, channel=None, reason=7):
        self.channel_lock.acquire()
        if channel:
            self.set_channel(channel)
        pkt = RadioTap() / Dot11(type=0, subtype=12, addr1=target_mac, addr2=source_mac,
                                 addr3=self.bssid) / Dot11Deauth(reason=reason)
        for i in range(count):
            cprint("DEAUTH!!!", 'red')
            for j in range(burst_count):
                self.inject(pkt)
            if count > 1:
                sleep(.1)
        self.channel_lock.release()

    def get_new_station(self) -> Station:
        self.sta_sema.acquire()
        target = next((self.stations[client] for client in self.stations if self.stations[client].new), None)
        target.new = False
        return target

    def get_new_ap(self) -> AP:
        self.ap_sema.acquire()
        target = next((self.aps[ap] for ap in self.aps if self.aps[ap].new), None)
        target.new = False
        return target

    def inject(self, pkt, inter=0):
        sendp(pkt, iface=self.name, inter=inter, verbose=False)

    def scan(self):
        self.scan_thread = ScannerThread(self)
        self.scan_thread.start()

    def stop_scan(self):
        self.scan_thread.stop()
        self.scan_thread.join()

    def ap_passes_test(self, pkt):
        return (pkt.haslayer(Dot11) and pkt.type == 0 and pkt.subtype == 8
                and not self.aps.get(pkt.addr3))

    def sta_passes_test(self, pkt):
        # Just for readability/sanity
        client_mgmt_subtypes = (0, 2, 4)
        check = False
        if pkt.haslayer(Dot11):
            if (pkt.type == 0 and (not self.bssid or pkt.addr3 == self.bssid)
                    and pkt.subtype in client_mgmt_subtypes):
                check = True
            elif pkt.type == 2 and (pkt.addr1 == self.bssid or not self.bssid):
                check = True
        if check:
            return not (self.stations.get(pkt.addr2) or self.stations.get(pkt.addr1))

    @staticmethod
    def sta_mac(pkt):
        return pkt.addr1 if not pkt.addr1 == pkt.addr3 else pkt.addr2

    def scan_callback(self, pkt):
        try:
            # Management/Beacon
            if self.ap_passes_test(pkt):
                self.lock.acquire()
                self.ap_sema.release()
                # http://stackoverflow.com/a/21664038
                essid, channel, w = None, None, None
                bssid = pkt.addr3
                crypto = ""
                cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}"
                                  "{Dot11ProbeResp:%Dot11ProbeResp.cap%}").split('+')
                p = pkt[Dot11Elt]
                while isinstance(p, Dot11Elt):
                    if p.ID == 0:
                        try:
                            essid = p.info.decode()
                        except UnicodeDecodeError as e:
                            print(p.info)
                            essid = p.info
                    elif p.ID == 3:
                        try:
                            channel = ord(p.info)
                        except TypeError as e:
                            print(p.info)
                            channel = p.info
                    elif p.ID == 48:
                        crypto = "WPA2"
                        w = p.info[18:19]
                    elif p.ID == 221 and p.info.startswith(b'\x00P\xf2\x01\x01\x00'):
                        crypto = "WPA"
                    p = p.payload
                if not crypto:
                    if 'privacy' in cap:
                        crypto = "WEP"
                    else:
                        crypto = "OPN"
                self.aps[bssid] = AP(bssid, essid, crypto, channel, w)
                self.lock.release()
            elif self.sta_passes_test(pkt):
                self.lock.acquire()
                try:
                    channel = pkt[Dot11Elt:3].info
                except IndexError:
                    channel = self.channel
                mac = self.sta_mac(pkt)
                self.stations[mac] = Station(mac, channel, pkt.addr3)
                self.sta_sema.release()
                self.lock.release()
        except Exception as e:
            print(pkt)
            raise e
