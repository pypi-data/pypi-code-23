import struct
import socket
from pcapfile import savefile


class PcapAnalyzer:

    @staticmethod
    def openFile(file):
        with open(file, 'rb') as f:
            return savefile.load_savefile(f, verbose=True)

    @staticmethod
    def to_dict(file):
        pcap_raw = PcapAnalizer.openFile(file)
        list_dict = []

        for pkg in pcap_raw.packets:
            list_dict.append(RawPkg.unpack(pkg.raw()))

        return list_dict


# Protocol identification
IPV4 = 8
ICMP = 1
TCP = 6
UDP = 17

# Byte Header
ETHERNET_H = 14
DATAGRAM_H = 20
ICMP_H = 4
TCP_H = 14
UDP_H = 8


class RawPkg:

    @staticmethod
    def unpack(pkg):
        infos = dict()

        infos['DATALINK'], payload = RawPkg.ethernet_frame(pkg)
        proto = infos['DATALINK']['proto']

        infos['NETWORK'], payload, carry_on = RawPkg.package(payload, proto)
        proto = infos['NETWORK']['proto']

        if carry_on:  # Then IPV4

            if proto == ICMP:
                infos['TRANSPORT'], data = RawPkg.icmp(payload)

            elif proto == TCP:
                infos['TRANSPORT'], data = RawPkg.tcp(payload)

            elif proto == UDP:
                infos['TRANSPORT'], data = RawPkg.udp(payload)

            else:
                infos['TRANSPORT'] = dict(protocol='Unkown')
                data = payload

            infos['data'] = data

        else:
            infos['data'] = payload

        return infos

    @staticmethod
    def MAC(bytes_addr):
        '''
        Format macaddress
        Arguments:
                    bytes_addr -- raw byte macaddress
        Returns:
                    mac_address -- str
        '''

        bytes_str = map('{:02x}'.format, bytes_addr)
        mac_address = ':'.join(bytes_str).upper()
        return mac_address

    @staticmethod
    def IPv4(addr):
        '''
            Format IPv4
            Arguments:
                        addr -- raw ipv4
            Returns:
                        ipv4 -- str
        '''
        ipv4 = '.'.join(map(str, addr))
        return ipv4

    @staticmethod
    def ethernet_frame(pkg):
        '''
        -- DataLink Layer ( OSI 2 ) --

        Arguments:
                    pkg -- raw byte pakages
        Returns:
                    eth_fram -- dict['source', 'destination', 'proto']
                    payload -- remaning payload from the ethernet frame
        '''

        destination, source, proto = struct.unpack(
            '! 6s 6s H', pkg[:ETHERNET_H])

        frame = dict(destination=RawPkg.MAC(destination),
                     source=RawPkg.MAC(source),
                     proto=socket.htons(proto))

        payload = pkg[ETHERNET_H:]

        return frame, payload

    @staticmethod
    def package(pkg, proto):
        '''
        -- Network Layer ( OSI 3 ) --

        Arguments:
                    pkg -- raw byte pakages
                    proto -- 8 for IPv4, else others
        Returns:
                    package -- dict['version','header_len','ttl'
                                    'source', 'destination', 'proto']
                    payload -- remaning payload from the datagram frame
                    carry_on -- bool
        '''

        if proto == IPV4:
            version_header_length = +pkg[0]
            version = version_header_length >> 4
            header_length = (version_header_length & 15) * 4
            ttl, proto, source, target = struct.unpack(
                '! 8x B B 2x 4s 4s', pkg[:DATAGRAM_H])

            package = dict(protocol='IPV4',
                           version=version,
                           header_len=header_length,
                           ttl=ttl,
                           proto=proto,
                           source=RawPkg.IPv4(source),
                           target=RawPkg.IPv4(target))

            payload = pkg[header_length:]
            carry_on = True

        else:
            package = dict(type='Unkwon',
                           proto=proto)
            payload = pkg
            carry_on = False

        return package, payload, carry_on

    @staticmethod
    def icmp(pkg):
        '''
            -- Transport Layer ( OSI 4 ) --

            Arguments:
                        pkg -- raw byte pakages

            Returns:
                        icmp -- dict['type', 'code','checksum']
                        payload -- remaning byte

        '''

        _type, code, checksum = struct.unpack('! B B H', pkg[:ICMP_H])

        icmp = dict(
            protocol='ICMP',
            type=_type,
            code=code,
            checksum=checksum)

        payload = pkg[ICMP_H:]

        return icmp, payload

    @staticmethod
    def tcp(pkg):
        '''
            -- Transport Layer ( OSI 4 ) --

            Arguments:
                        pkg -- raw byte pakages

            Returns:
                        segment -- dict['source', 'destination','sequence','ack','flags']
                        payload -- data

        '''

        (src_port, dest_port, sequence, ack, offset_reserved_flags) = struct.unpack(
            '! H H L L H', pkg[:TCP_H])
        offset = (offset_reserved_flags >> 12) * 4
        urg = (offset_reserved_flags & 32) >> 5
        ack = (offset_reserved_flags & 16) >> 5
        psh = (offset_reserved_flags & 8) >> 5
        rst = (offset_reserved_flags & 4) >> 5
        syn = (offset_reserved_flags & 2) >> 5
        fin = offset_reserved_flags & 1 >> 5

        segment = dict(protocol='TCP',
                       source=src_port,
                       destination=dest_port,
                       sequence=sequence,
                       ack=ack,
                       flags=dict(urg=urg,
                                  ack=ack,
                                  psh=psh,
                                  rst=rst,
                                  syn=syn,
                                  fin=fin))
        payload = pkg[offset:]

        return segment, payload

    @staticmethod
    def udp(pkg):
        '''
            -- Transport Layer ( OSI 4 ) --

            Arguments:
                        pkg -- raw byte pakages

            Returns:
                        segment -- dict['source', 'destination','size']
                        payload -- data

        '''
        src_port, dest_port, size = struct.unpack('! H H 2x H', pkg[:UDP_H])

        datagram = dict(protocol='UDP', source=src_port,
                        destination=dest_port, size=size)
        payload = pkg[UDP_H:]

        return datagram, payload
