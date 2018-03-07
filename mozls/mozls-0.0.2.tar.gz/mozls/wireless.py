import re
from subprocess import check_output

from mozls.location import WifiNetwork

IW_BSSID_REGEX = "((?<=BSS )([0-9a-f]{2}:){5}([0-9a-f]{2}))"
IW_SIGNAL_REGEX = "((?<=	signal: )-[0-9]{2})"


class ParseError(Exception):
    pass


def scan_wireless_networks(interface: str) -> WifiNetwork:
    call = ["iw", "dev", interface, "scan"]

    iw_output = bytes.decode(check_output(call))

    bssid_re = re.compile(IW_BSSID_REGEX, flags=re.MULTILINE)
    signal_re = re.compile(IW_SIGNAL_REGEX, flags=re.MULTILINE)

    bssids = list(filter(lambda x: len(x) == 3, bssid_re.findall(iw_output)))
    signals = signal_re.findall(iw_output)

    if len(bssids) is not len(signals):
        raise ParseError

    out = []
    for bssid, signal in zip(bssids, signals):
        out.append(WifiNetwork(mac_address=bssid[0], signalStrength=int(signal)))
    return out
