# -*- coding: utf-8 -*-
"""iceman/traffic/traffic.py
"""
import copy
from multiprocessing import Manager, Queue, Lock
from socket import inet_ntop, AF_INET
import sys

from dpkt import ip, tcp
import nfqueue
from termcolor import colored


class Traffic(object):
    """IP Packet Traffic Judge

    :param egress_queue: nfqueue number
    :type egress_queue: int

    :param ingress_queue: nfqueue number
    :type ingress_queue: int

    :param cipher_suite: crypto wrapper cipher strategy
    :type cipher_suite: instance

    :param encryption_enabled: encryption flag
    :type encryption_enabled: bool
    """

    def __init__(self, egress_queue, ingress_queue, cipher_suite, encryption_enabled):

        self.egress_queue = egress_queue
        self.ingress_queue = ingress_queue
        self.cipher_suite = cipher_suite
        self.encryption_enabled = encryption_enabled

        #TODO optimize thread-locking for multiple clients, use new
        #  Manager.dict() dictionaries for tcp_states instead of one giant dictionary
        self.mgr = Manager()

        #dictionary for containing tcp connection states and relevant data
        self.tcp_states = self.mgr.dict()
        self.tcp_state_lock = self.mgr.Lock()
        #TODO create a per socket pair lock?

        #test variables
        self.counter = self.mgr.Value('i', 0)
        self.ecounter = self.mgr.Value('i', 0)
        self.icounter = self.mgr.Value('i', 0)

        self.log_glob = Queue()
        self.log_lock = Lock()


    def create_socket_dict(self):
        """blank TCP connection data dictionary
        """
        return {    #TODO - clean up unused parameters - current list:
                    #       enc?dec?.una, wnd?, enc.iss and enc.irs (same for both)
            'enc' : {           # encrypted parameters
                'snd' : {
                    'una' : 0,  # unACK'd byte index
                    'wnd' : 0,  # size of window - TODO is it remote's or host's defined window?
                    'nxt' : 0,  # predicted/acceptable next message byte index
                    'iss' : 0   # initial sequence number
                },
                'rcv' : {
                    'irs' : 0,  # initial acknowledgement number
                    'wnd' : 0,  # size of window - TODO is it remote's or host's defined window?
                    'nxt' : 0   # predicted/acceptable next message byte index,
                                #   LHS of missing packet gap (when out of order)
                },
                'unachk' : {},  # set of rcvd encrypted SEQ numbers to check
                                #   incoming pkt.SEQs against, helps translate
                                #   older rexmit pkts SEQ numbers
                'ackchk' : {}   # set of encrypted SEQ numbers to check incoming pkt.ACKs against,
                                #   helps find which pkts were ACK'd
            },
            'dec' : {               #decrypted parameters
                'snd' : {
                    'una' : 0,
                    'wnd' : 0,
                    'nxt' : 0,
                    'iss' : 0,
                    'valid-ack' : 0 # last ACK # emitted by the app layer
                                    #    (used as a lower bound for comparing ACK ids)
                },
                'rcv' : {
                    'irs' : 0,
                    'wnd' : 0,
                    'nxt' : 0
                },
                'ackchk' : {}  # set of decrypted rcv.SEQ numbers to check incoming snd.ACKs against,
                               #    helps find which pkts were ACK'd
                               # structure: [(dec.rcv.SEQ + pktlen + flaginc)(OR)dec.snd.ACK] =
                               #    (enc.rcv.SEQ + pktlen + flaginc)(OR)dec.snd.ACK
            },
            'rexmit' : {},         # dictionary of sent messages to check if it's a retransmission,
                                   #    removed when ACK'd by client
            'remote-special' : {}, # special messages rcv'd by host from remote (i.e. FIN)
            'host-close' : False,   # flag for host attempting to close
            'remote-close' : False, # flag for remote attempting to close
            'last-update' : 0       # counter for incrementing to check if the socket data was altered
        }


    def merge_tcp_data(self, index, old, new, orig):
        """merges tcp data dictionaries
        """
        #assumes tcpstatelock has already been acquired
        #TODO handle wraparound cases for SEQ ACK #'s

        if old['last-update'] > new['last-update']:
            #complicated, need to merge the two dictionaries now
            #3 states - new is fresher than old, use new data
            #           new is staler than old (i.e. unchanged data), use old data
            #           both have fresh and competing data, merge data somehow
            #TODO check all possible combinations of SND and RCV values
            #  to make sure one doesnt get overwritten by accident

            new['last-update'] = old['last-update']
            if old['enc']['snd']['nxt'] > new['enc']['snd']['nxt']:
                new['enc']['snd'] = old['enc']['snd']
            if old['dec']['snd']['nxt'] > new['dec']['snd']['nxt']:
                new['dec']['snd'] = old['dec']['snd']

            if old['enc']['rcv']['nxt'] > new['enc']['rcv']['nxt']:
                new['enc']['rcv'] = old['enc']['rcv']
            if old['dec']['rcv']['nxt'] > new['dec']['rcv']['nxt']:
                new['dec']['rcv'] = old['dec']['rcv']

            #for dictionaries, highest SEQ entry has priority, keep self (i.e. highest SEQ) from other dictionary
            new['enc']['ackchk'] = self.merge_tcp_dictionary(
                old['enc']['ackchk'],
                new['enc']['ackchk'],
                orig['enc']['ackchk']
            )
            new['enc']['unachk'] = self.merge_tcp_dictionary(
                old['enc']['unachk'],
                new['enc']['unachk'],
                orig['enc']['unachk']
            )
            new['dec']['ackchk'] = self.merge_tcp_dictionary(
                old['dec']['ackchk'],
                new['dec']['ackchk'],
                orig['dec']['ackchk']
            )
            new['rexmit'] = self.merge_tcp_dictionary(
                old['rexmit'],
                new['rexmit'],
                orig['rexmit']
            )
            new['remote-special'] = self.merge_tcp_dictionary(
                old['remote-special'],
                new['remote-special'],
                orig['remote-special']
            )

            #if either one is true, set to true
            new['host-close'] = new['host-close'] if new['host-close'] else old['host-close']
            new['remote-close'] = new['remote-close'] if new['remote-close'] else old['remote-close']
        else:
            #simple case, just overwrite
            pass

        new['last-update'] += 1

        #overwrite old data with new merged data
        self.tcp_states[index] = new


    def merge_tcp_dictionary(self, old, new, orig):
        """merges a given dictionary with the old (external updates),
        new (self updates),
        and original (original state) dictionaries
        """
        retval = new #default case

        old_max = 0
        new_max = 0
        orig_max = 0

        #if not empty, use max
        if old:
            old_max = max(old, key=int)
        if new:
            new_max = max(new, key=int)
        if orig:
            orig_max = max(orig, key=int)

        self.print_debug(
            colored(
                "?-TEST->TCPMERGE MAXVALS old-%s, new-%s, orig-%s" % (
                    old_max,
                    new_max,
                    orig_max
                ),
                'magenta'
            )
        )

        #special case if a dict is empty (max == 0)
        if orig_max == 0:
            #make sure no max's are used which = 0
            if new_max == 0:
                #use old, even if old is 0
                retval = old
            elif old_max == 0:
                #use new, even if new is 0
                retval = new
            else:
                #normal check, whichever is greater, and keep max entry of both
                if old_max > new_max:
                    old[new_max] = new[new_max]
                    retval = old
                elif old_max < new_max:
                    new[old_max] = old[old_max]
                    retval = new
                else:
                    #TODO both MAY have the same data here, could be odd, might want to check some assertions
                    if old[old_max] != new[new_max]:
                        self.print_debug(
                            colored(
                                "?-TEST(%03d)->TCPMERGE old{%s : %s} new{%s : %s} USING NEW" % (
                                    self.ecounter.value,
                                    old_max,
                                    old[old_max],
                                    new_max,
                                    new[new_max]
                                ),
                                'magenta'
                            )
                        )
                        #TODO how to handle this?
                        #use default case for now
                        retval = new
                    else:
                        #just pick one
                        retval = new
        else:
            if new_max == 0:
                #means new deleted something
                if old_max == orig_max:
                    #old is stale, delete everything
                    retval = new
                else:
                    #just use old, even if old is 0
                    retval = old
            elif old_max == 0:
                #means old deleted something
                if new_max == orig_max:
                    #old is stale, delete everything
                    retval = new
                else:
                    #just use new, even if new is 0
                    retval = new
            else:
                #both old and new have new data from a blank dictionary
                #normal check, whichever is greater, and keep max entry of both
                if old_max > new_max:
                    old[new_max] = new[new_max]
                    retval = old

                elif old_max < new_max:
                    new[old_max] = old[old_max]
                    retval = new

                else:
                    #TODO both MAY have the same data here, could be odd, might want to check some assertions
                    if old[old_max] != new[new_max]:
                        self.print_debug(
                            colored(
                                "?-TEST(%03d)->TCPMERGE old{%s : %s} new{%s : %s}" % (
                                    self.ecounter.value,
                                    old_max,
                                    old[old_max],
                                    new_max,
                                    new[new_max]
                                ),
                                'magenta'
                            )
                        )

                        #TODO how to handle this?
                        #use default case for now
                        retval = new

                    else:
                        #just pick one
                        retval = new

        return retval

    def handle_egress(self, not_used, payload): # pylint: disable=unused-argument
                                                # pylint: disable-msg=R0915
        """egress traffic handler
        """
        pkt = ip.IP(payload.get_data())

        new_conn = False
        rst_conn = False
        is_rexmit = False
        flaginc = 0

        self.ecounter.value += 1

        #get socket pair TCP data
        tcp_index = (pkt.src, pkt.tcp.sport, pkt.dst, pkt.tcp.dport)
        tcp_data = {}

        self.print_debug(
            "E-tcp_data(%03d): [%s:%s - %s:%s]" % (
                self.ecounter.value,
                inet_ntop(AF_INET, pkt.src),
                str(pkt.tcp.sport),
                inet_ntop(AF_INET, pkt.dst),
                str(pkt.tcp.dport)
            )
        )

        self.tcp_state_lock.acquire()

        #has_key sometimes fails for some reason
        tmpdict = self.tcp_states.get(tcp_index, None)
        if tmpdict is not None:
            tcp_data = tmpdict

        else:
            tcp_data = self.create_socket_dict()
            self.tcp_states[tcp_index] = tcp_data
            self.print_debug(
                colored(
                    "EGRESS: INITIALIZING SOCKET PAIR: [%s:%s - %s:%s]" % (
                        inet_ntop(AF_INET, pkt.src),
                        str(pkt.tcp.sport),
                        inet_ntop(AF_INET, pkt.dst),
                        str(pkt.tcp.dport)
                    ),
                    'cyan'
                )
            )
            new_conn = True

        self.tcp_state_lock.release()
        #make sure to deep copy the data for the original, no sneaky accidental updates
        tcp_data_orig = copy.deepcopy(tcp_data)
        self.print_tcp_data(tcp_data, self.ecounter.value, 'E-TEST')

        #Handle special cases
        pktlen = len(pkt.tcp.data)
        seqdiff = pkt.tcp.seq - tcp_data['dec']['snd']['iss']
        ackdiff = pkt.tcp.ack - tcp_data['dec']['rcv']['irs']
        decseq = pkt.tcp.seq
        decack = pkt.tcp.ack

        #Check if reXmit, if not then add to reXmit
        if pkt.tcp.seq in tcp_data['rexmit']:
            #Check if SEQ # is lower than previous SEQ #'s
            # some 0 length packets increment SEQ, most ACKs are disposable/transient
            if (pkt.tcp.seq - tcp_data['dec']['snd']['nxt'] < 0) and tcp_data['rexmit'][pkt.tcp.seq] != 0:
                self.print_debug(
                    colored(
                        "E-TEST(%03d)->SEG(SEQ=%s, ACK=%s, LEN=%s) [%s] REXMIT" % (
                            self.ecounter.value,
                            seqdiff,
                            ackdiff,
                            pktlen,
                            self.get_flag_string(pkt)
                        ),
                        'cyan'
                    )
                )

                #Don't update any state variables, rexmit is just sending old data with SOME updated vars (i.e. ACK#)
                pkt.tcp.seq = tcp_data['rexmit'][pkt.tcp.seq][2]

                hacklen = 0
                if pktlen > 0:
                    tcp_data['dec']['snd']['nxt'] += pktlen

                    #PACKET MOD!
                    if self.encryption_enabled:
                        try:
                            pkt.tcp.data = self.cipher_suite.encrypt(pkt.tcp.data)
                        except Exception as ex: # pylint: disable=broad-except
                            self.print_debug(
                                colored(
                                    "E-CIPHER(%03d)->ERROR ENCRYPTING: [%s]" % (
                                        self.ecounter.value,
                                        ex
                                    ),
                                    'red'
                                )
                            )

                    #TODO store packet padding since re-encrypting the packet
                    #   will NOT result in the same padding length...
                    hacklen = len(pkt.tcp.data) - pktlen

                    pkt.len += hacklen
                    tcp_data['enc']['snd']['nxt'] += pktlen + hacklen

                #get ACK from ackchk
                if pkt.tcp.ack in tcp_data['dec']['ackchk']:
                    self.print_debug(
                        "E-HACK(%03d)->REXMIT ACKCHK FOUND! %s->%s" % (
                            self.ecounter.value,
                            ackdiff,
                            tcp_data['dec']['ackchk'][pkt.tcp.ack] - tcp_data['dec']['rcv']['irs']
                        )
                    )
                    pkt.tcp.ack = tcp_data['dec']['ackchk'][pkt.tcp.ack]
                    #remove ackchks less than the currently ACK'd key
                    for key in tcp_data['dec']['ackchk'].keys():
                        if key < decack:
                            self.print_debug(
                                "E-HACK(%03d)->REXMIT ACKCHK-DEL [%s %s]" % (
                                    self.ecounter.value,
                                    key,
                                    str(tcp_data['dec']['ackchk'][key])
                                )
                            )
                            del tcp_data['dec']['ackchk'][key]

                #clear checksums to recalculate
                pkt.tcp.sum = 0
                pkt.sum = 0

                self.print_debug(
                    colored(
                        "E-HACK(%03d)->SEG(SEQ=%+d, ACK=%+d, LEN=%+d) [%s]" % (
                            self.ecounter.value,
                            pkt.tcp.seq - decseq,
                            pkt.tcp.ack - decack,
                            len(pkt.tcp.data) - pktlen,
                            self.get_flag_string(pkt)
                        ),
                        'green'
                    )
                )

                payload.set_verdict_modified(
                    nfqueue.NF_ACCEPT,
                    str(pkt),
                    len(pkt)
                )

                return 1

        if self.has_flag(pkt, tcp.TH_RST):
            #TODO figure out what a reset sets for ACK/SEQ #'s
            #RST, if valid, can only result in a state of CLOSED

            self.print_debug(
                colored(
                    "E-TEST->RST sent",
                    'red'
                )
            )
            tcp_data['dec']['rcv']['irs'] = pkt.tcp.ack
            tcp_data['dec']['rcv']['nxt'] = pkt.tcp.ack

            tcp_data['enc']['rcv']['irs'] = pkt.tcp.ack
            tcp_data['enc']['rcv']['nxt'] = pkt.tcp.ack
            #NOTE ACK # in egress may be 0
            rst_conn = True

        elif self.has_flag(pkt, tcp.TH_SYN):
            #set the initial variables and SEQ numbers
            tcp_data['dec']['snd']['iss'] = pkt.tcp.seq
            tcp_data['dec']['snd']['una'] = pkt.tcp.seq
            tcp_data['dec']['snd']['nxt'] = pkt.tcp.seq + 1

            tcp_data['enc']['snd']['iss'] = pkt.tcp.seq
            tcp_data['enc']['snd']['una'] = pkt.tcp.seq
            tcp_data['enc']['snd']['nxt'] = pkt.tcp.seq
            flaginc = 1

        elif self.has_flag(pkt, tcp.TH_FIN):
            #required to increment even if no data in order to acknowledge FIN
            tcp_data['dec']['snd']['nxt'] += 1
            flaginc = 1

        elif new_conn:
            #rcvd pkt when skt was not open...
            self.print_debug(
                colored(
                    "E-TEST(%03d)->CLOSED HOST SKT SENDING PKT(!SYN)? MAJOR ERROR" % (
                        self.ecounter.value
                    ),
                    'red'),
                True
            )

        #Check assertions
        self.print_debug(
            colored(
                "E-TEST(%03d)->SEG(SEQ=%s, ACK=%s, LEN=%s) [%s]" % (
                    self.ecounter.value,
                    seqdiff,
                    ackdiff,
                    pktlen,
                    self.get_flag_string(pkt)
                ),
                'yellow'
            )
        )

        if tcp_data['dec']['rcv']['nxt'] == pkt.tcp.ack:
            #self.print_debug("E-TEST->SEG(ACK) == RCV.NXT")
            #set ack normally
            pkt.tcp.ack = tcp_data['enc']['rcv']['nxt']

            #remove rcvd packets that are ACKd by this outgoing packet
            if pkt.tcp.ack in tcp_data['enc']['unachk']:
                for key in tcp_data['enc']['unachk'].keys():
                    if key < pkt.tcp.ack:
                        del tcp_data['enc']['unachk'][key]
        else:
            #app layer is not ACKing all the packets we've rcvd
            #maybe it hasn't processed everything, maybe there was an error...
            self.print_debug(
                colored(
                    "E-TEST(%03d)->SEG(ACK) != RCV.NXT [%s]" % (
                        self.ecounter.value,
                        pkt.tcp.ack - tcp_data['dec']['rcv']['nxt']
                    ),
                    'red'
                )
            )

            #check if its ACKing an older packet
            if pkt.tcp.ack in tcp_data['dec']['ackchk']:
                #found the older packet id, alter the ACK accordingly and cleanup the older out of scope packets
                self.print_debug(
                    "E-HACK(%03d)->ACKCHK FOUND! %s->%s" % (
                        self.ecounter.value,
                        ackdiff,
                        tcp_data['dec']['ackchk'][pkt.tcp.ack] - tcp_data['dec']['rcv']['irs']
                    )
                )

                pkt.tcp.ack = tcp_data['dec']['ackchk'][pkt.tcp.ack]
                #remove ackchks less than the currently ACK'd key
                for key in tcp_data['dec']['ackchk'].keys():
                    if key < decack:
                        self.print_debug(
                            "E-HACK(%03d)->ACKCHK-DEL [%s %s]" % (
                                self.ecounter.value,
                                key,
                                str(tcp_data['dec']['ackchk'][key])
                            )
                        )
                        del tcp_data['dec']['ackchk'][key]

            elif not new_conn:
                #older packet wasn't found
                #TODO handle this error case
                self.print_debug(
                    colored(
                        "E-HACK(%03d)->ACKCHK NOT FOUND! %s - %s" % (
                            self.ecounter.value,
                            pkt.tcp.ack,
                            str(tcp_data['dec']['ackchk'])
                        ),
                        'red'
                    ),
                    True
                )

        #Modify Packet
        if tcp_data['dec']['snd']['nxt'] == pkt.tcp.seq + flaginc: #HACK add flaginc to check prior snd.nxt value
            #self.print_debug("E-TEST->SEG(SEQ) == SND.NXT")
            pass

        else:
            self.print_debug(
                colored(
                    "E-TEST(%03d)->SEG(SEQ) != SND.NXT [%s]" % (
                        self.ecounter.value,
                        pkt.tcp.seq - tcp_data['dec']['snd']['nxt']
                    ),
                    'red'
                )
            )

        #TODO handle ACK/SEQ wraparound cases
        pkt.tcp.seq = tcp_data['enc']['snd']['nxt']
        hacklen = 0

        if pktlen > 0:
            tcp_data['dec']['snd']['nxt'] += pktlen

            #PACKET MOD!
            if self.encryption_enabled:
                try:
                    pkt.tcp.data = self.cipher_suite.encrypt(pkt.tcp.data)
                except Exception as ex: # pylint: disable=broad-except
                    self.print_debug(
                        colored(
                            "E-CIPHER(%03d)->ERROR ENCRYPTING: [%s]" % (
                                self.ecounter.value,
                                ex
                            ),
                            'red'
                        )
                    )

            #pktlen % 10 #forces hacklen to be a function of the pktlen itself, similar to how the true cipher works...
            hacklen = len(pkt.tcp.data) - pktlen

            pkt.len += hacklen
            tcp_data['enc']['snd']['nxt'] += pktlen + hacklen

        #clear checksums to recalculate
        pkt.tcp.sum = 0
        pkt.sum = 0

        #Update encrypted state variables
        if not is_rexmit:
            #add pkt seq # to
            # TODO EM - let's put this index into a variable to make sense of it
            tcp_data['enc']['ackchk'][pkt.tcp.seq + flaginc + pktlen + hacklen] = decseq + flaginc + pktlen
            tcp_data['enc']['snd']['nxt'] += flaginc
            tcp_data['rexmit'][decseq] = (decack, pkt.tcp.flags, pkt.tcp.seq)

        #Check if any special packets from remote were ACK'd
        for key in tcp_data['remote-special'].keys():
            if key < pkt.tcp.ack:
                #assume only FIN packets are here
                tcp_data['remote-close'] = True
                self.print_debug(
                    "E-TEST(%03d)->HOST ACK'd REMOTE's FIN" % (
                        self.ecounter.value
                    )
                )
                del tcp_data['remote-special'][key]

        #check if the socket was closed
        self.tcp_state_lock.acquire()
        if (tcp_data['host-close'] and tcp_data['remote-close']) or rst_conn:
            self.print_debug(
                colored(
                    "E-TEST(%03d)->SKT CLOSED" % (
                        self.ecounter.value
                    ),
                    'cyan'
                )
            )
            del self.tcp_states[tcp_index]
        else:
            #Update stored TCP Data with any changes
            #handles case wherekvp gets deleted during packet processing (socket was cleaned up)
            if tcp_index in self.tcp_states:
                tcp_data_old = self.tcp_states[tcp_index]
                self.print_tcp_data(tcp_data_old, self.ecounter.value, 'E-LATE')
                self.merge_tcp_data(tcp_index, tcp_data_old, tcp_data, tcp_data_orig)
            else:
                self.print_debug(
                    colored(
                        "E-HACK(%03d)->TCPDATA DELETED FOR [%s:%s - %s:%s]" % (
                            self.ecounter.value,
                            inet_ntop(AF_INET, pkt.src),
                            str(pkt.tcp.sport),
                            inet_ntop(AF_INET, pkt.dst),
                            str(pkt.tcp.dport)
                        ),
                        'green'
                    )
                )

        self.tcp_state_lock.release()

        self.print_debug(
            "E-UPDATE tcp_data(%03d)" % (
                self.ecounter.value
            )
        )

        self.print_tcp_data(tcp_data, self.ecounter.value, 'E-TEST')

        self.print_debug(
            colored(
                "E-HACK(%03d)->SEG(SEQ=%+d, ACK=%+d, LEN=%+d) [%s]" % (
                    self.ecounter.value,
                    pkt.tcp.seq - decseq,
                    pkt.tcp.ack - decack,
                    len(pkt.tcp.data) - pktlen,
                    self.get_flag_string(pkt)
                ),
                'green'
            )
        )

        payload.set_verdict_modified(nfqueue.NF_ACCEPT, str(pkt), len(pkt))


    def handle_ingress(self, not_used, payload): #pylint: disable=unused-argument
                                                # pylint: disable-msg=R0915
        """nfqueue callback
        """
        pkt = ip.IP(payload.get_data())

        new_conn = False
        rst_conn = False
        is_rexmit = False
        flaginc = 0

        self.icounter.value += 1
        #get socket pair TCP data
        tcp_index = (pkt.dst, pkt.tcp.dport, pkt.src, pkt.tcp.sport)
        tcp_data = {}
        self.tcp_state_lock.acquire()

        tmpdict = self.tcp_states.get(tcp_index, None)
        if tmpdict is not None:
            tcp_data = tmpdict

        else:
            tcp_data = self.create_socket_dict()
            self.tcp_states[tcp_index] = tcp_data

            self.print_debug(
                colored(
                    "INGRESS: INITIALIZING SOCKET PAIR: [%s:%s - %s:%s]" % (
                        inet_ntop(AF_INET, pkt.dst),
                        str(pkt.tcp.dport),
                        inet_ntop(AF_INET, pkt.src),
                        str(pkt.tcp.sport)
                    ),
                    'cyan'
                )
            )

            new_conn = True

        self.tcp_state_lock.release()
        tcp_data_orig = copy.deepcopy(tcp_data)

        self.print_debug(
            "I-tcp_data(%03d): [%s:%s - %s:%s]" % (
                self.icounter.value,
                inet_ntop(AF_INET, pkt.dst),
                str(pkt.tcp.dport),
                inet_ntop(AF_INET, pkt.src),
                str(pkt.tcp.sport)
            )
        )

        self.print_tcp_data(tcp_data, self.icounter.value, 'I-TEST')

        #Handle special cases
        #TODO check if reXmit

        if self.has_flag(pkt, tcp.TH_RST):
            #TODO figure out what a reset sets for ACK/SEQ #'s
            #TODO should RST get sent into the remote-special queue? Does the host ACK RST packets?

            self.print_debug(
                colored(
                    "I-TEST(%03d)->RST rcvd, closing SKT" % (
                        self.icounter.value
                    ),
                    'red'
                )
            )

            rst_conn = True
            #NOTE SEQ # in ingress may be 0

        elif self.has_flag(pkt, tcp.TH_SYN):
            tcp_data['dec']['rcv']['irs'] = pkt.tcp.seq
            tcp_data['dec']['rcv']['nxt'] = pkt.tcp.seq

            tcp_data['enc']['rcv']['irs'] = pkt.tcp.seq
            tcp_data['enc']['rcv']['nxt'] = pkt.tcp.seq
            flaginc = 1

        elif self.has_flag(pkt, tcp.TH_FIN):
            # tcp_data['remote-close'] = True
            tcp_data['remote-special'][pkt.tcp.seq] = (pkt.tcp.ack, pkt.tcp.flags)

            self.print_debug(
                "I-TEST(%03d)->REMOTE CLOSING" % (
                    self.icounter.value
                )
            )

            flaginc = 1

        elif new_conn:
            #rcvd pkt when skt was not open...
            self.print_debug(
                colored(
                    "I-TEST(%03d)->CLOSED SKT RCVD PKT(!SYN), RESET?" % (
                        self.icounter.value
                    ),
                    'red'
                )
            )

        #Check assertions update SOME state variables
        pktlen = len(pkt.tcp.data)

        # TODO EM - this isn't used
        #seqdiff = pkt.tcp.seq - tcp_data['dec']['rcv']['irs']

        ackdiff = pkt.tcp.ack - tcp_data['dec']['snd']['iss']
        encseqdiff = pkt.tcp.seq - tcp_data['enc']['rcv']['irs']
        encackdiff = pkt.tcp.ack - tcp_data['enc']['snd']['iss']
        encseq = pkt.tcp.seq
        encack = pkt.tcp.ack

        self.print_debug(
            colored(
                "I-TEST(%03d)->SEG(SEQ=%s, ACK=%s, LEN=%s) [%s]" % (
                    self.icounter.value,
                    encseqdiff,
                    encackdiff,
                    pktlen,
                    self.get_flag_string(pkt)
                ),
                'yellow'
            )
        )

        if tcp_data['enc']['rcv']['nxt'] == pkt.tcp.seq:
            #next continuous packet, normal
            tcp_data['enc']['unachk'][pkt.tcp.seq] = tcp_data['dec']['rcv']['nxt']
            tcp_data['enc']['rcv']['nxt'] = pkt.tcp.seq + pktlen
            pkt.tcp.seq = tcp_data['dec']['rcv']['nxt']

        #possible out of order packet
        elif tcp_data['enc']['rcv']['nxt'] < pkt.tcp.seq:
            self.print_debug(
                colored(
                    "I-TEST(%03d)->SEG(SEQ) OOO? - DROP: %s" % (
                        self.icounter.value,
                        pkt.tcp.seq - tcp_data['enc']['rcv']['nxt']
                    ),
                    'green'
                )
            )
            #must drop, cant figure out dec.SEQ at this time
            #TODO parse ICE header or other ancillary info if possible to grab DEC.SEQ number
            payload.set_verdict(nfqueue.NF_DROP)
            return 0

        else:
            #packet already rcvd, dropping
            if pkt.tcp.seq in tcp_data['enc']['unachk']:
                self.print_debug(
                    "I-TEST(%03d)->SEG(SEQ) OLD/REPEAT UNACHK FOUND" % (
                        self.icounter.value
                    )
                )

                pkt.tcp.seq = tcp_data['enc']['unachk'][pkt.tcp.seq]
                #dont increment any state variables after this
                is_rexmit = True

            else:
                #TODO check if special flags might get dropped here...
                self.print_debug(
                    colored(
                        "I-TEST(%03d)->SEG(SEQ) OLD/REPEAT UNACHK NOT FOUND - DROP %+d" % (
                            self.icounter.value,
                            pkt.tcp.seq - tcp_data['enc']['rcv']['nxt']
                        ),
                        'red'
                    ),
                    True
                )

                payload.set_verdict(nfqueue.NF_DROP)
                return 0

        if tcp_data['enc']['snd']['una'] < pkt.tcp.ack:
            tcp_data['enc']['snd']['una'] = pkt.tcp.ack

        elif tcp_data['enc']['snd']['una'] == pkt.tcp.ack:
            if tcp_data['enc']['snd']['una'] == tcp_data['enc']['snd']['nxt']:
                self.print_debug(
                    "I-TEST(%03d)->SEG(ACK) No new data to ACK" % (
                        self.icounter.value
                    )
                )

            else:
                self.print_debug(
                    colored(
                        "I-TEST(%03d)->SEG(ACK) Duplicate ACK" % (
                            self.icounter.value
                        ),
                        'cyan'
                    )
                )

        else:
            self.print_debug(
                colored(
                    "I-TEST(%03d)->SEG(ACK) Bad ACK? Decreased in value...%s" % (
                        self.icounter.value,
                        pkt.tcp.ack - tcp_data['enc']['snd']['una']
                    ),
                    'red'
                ),
                True
            )

        #Modify packet
        if pktlen > 0:
            if self.encryption_enabled:
                try:
                    pkt.tcp.data = self.cipher_suite.decrypt(pkt.tcp.data)
                except Exception as ex: # pylint: disable=broad-except
                    self.print_debug(
                        colored(
                            "I-CIPHER(%03d)->ERROR DECRYPTING: [%s]" % (
                                self.icounter.value,
                                ex
                            ),
                            'red'
                        )
                    )

            hacklen = pktlen - len(pkt.tcp.data)
            pkt.len -= hacklen
            tcp_data['dec']['rcv']['nxt'] += len(pkt.tcp.data)

        if pkt.tcp.ack in tcp_data['enc']['ackchk']:
            self.print_debug(
                "I-HACK(%03d)->ACKCHK FOUND! %s->%s" % (
                    self.icounter.value,
                    ackdiff,
                    tcp_data['enc']['ackchk'][pkt.tcp.ack] - tcp_data['dec']['snd']['iss']
                )
            )
            pkt.tcp.ack = tcp_data['enc']['ackchk'][pkt.tcp.ack]

            #remove ackchks less than the currently ACK'd key
            for key in tcp_data['enc']['ackchk'].keys():
                if key < encack:
                    self.print_debug(
                        "I-HACK(%03d)->ACKCHK-DEL [%s %s]" % (
                            self.icounter.value,
                            key,
                            str(tcp_data['enc']['ackchk'][key])
                        )
                    )

                    del tcp_data['enc']['ackchk'][key]

        elif not new_conn:
            self.print_debug(
                colored(
                    "I-HACK(%03d)->ACKCHK NOT FOUND! %s - %s" % (
                        self.icounter.value,
                        pkt.tcp.ack,
                        str(tcp_data['enc']['ackchk'])
                    ),
                    'red'
                ),
                True
            )

        #clear checksums
        pkt.tcp.sum = 0
        pkt.sum = 0

        #Update State variables
        #minor assumption that FIN and SYN cannot be on the same packet
        tcp_data['dec']['rcv']['nxt'] += flaginc
        tcp_data['enc']['rcv']['nxt'] += flaginc

        ackchkndx = pkt.tcp.seq + flaginc + len(pkt.tcp.data)
        ackchkval = encseq + flaginc + pktlen

        self.print_debug(
            "I-TEST(%03d)->ACKCHK-ADD [%s %s]" % (
                self.icounter.value,
                ackchkndx,
                ackchkval
            )
        )

        tcp_data['dec']['ackchk'][ackchkndx] = ackchkval
        # structure: [(dec.rcv.SEQ + pktlen + flaginc)(OR)dec.snd.ACK] = (enc.rcv.SEQ + pktlen + flaginc)(OR)dec.snd.ACK

        #Remove ACK'd packets from reXmit queue
        for key in tcp_data['rexmit'].keys():
            if key < pkt.tcp.ack:
                if self.has_flag_simple(tcp_data['rexmit'][key][1], tcp.TH_FIN):
                    tcp_data['host-close'] = True

                    self.print_debug(
                        "I-TEST(%03d)->REMOTE ACK'd HOST's FIN" % (
                            self.icounter.value
                        )
                    )

                self.print_debug(
                    "I-TEST(%03d)->ACK-DEL [%s %s]" % (
                        self.icounter.value,
                        key,
                        str(tcp_data['rexmit'][key])
                    )
                )

                del tcp_data['rexmit'][key]

        #check if the connection is supposed to close
        self.tcp_state_lock.acquire()

        if (tcp_data['host-close'] and tcp_data['remote-close']) or rst_conn:
            self.print_debug(
                colored(
                    "I-TEST(%03d)->SKT CLOSED" % (
                        self.icounter.value
                    ),
                    'cyan'
                )
            )
            del self.tcp_states[tcp_index]

        #don't update state vars if it was a rexmit, should already have latest info
        elif not is_rexmit:
            #Update stored TCP Data with any changes
            tcp_data_old = self.tcp_states[tcp_index]
            self.print_tcp_data(tcp_data_old, self.icounter.value, 'I-LATE')
            self.merge_tcp_data(tcp_index, tcp_data_old, tcp_data, tcp_data_orig)

        self.tcp_state_lock.release()

        self.print_debug(
            "I-UPDATE tcp_data(%03d)" % (
                self.icounter.value
            )
        )
        self.print_tcp_data(tcp_data, self.icounter.value, 'I-TEST')


        self.print_debug(
            colored(
                "I-HACK(%03d)->SEG(SEQ=%+d, ACK=%+d, LEN=%+d) [%s]" % (
                    self.icounter.value,
                    pkt.tcp.seq - encseq,
                    pkt.tcp.ack - encack,
                    len(pkt.tcp.data) - pktlen,
                    self.get_flag_string(pkt)
                ),
                'green'
            )
        )

        payload.set_verdict_modified(nfqueue.NF_ACCEPT, str(pkt), len(pkt))


    def get_flag_string(self, pkt):
        """returns the flags applicable given a packet
        """

        return self.get_flag_string_simple(pkt.tcp.flags)


    def get_flag_string_simple(self, flags):
        """returns a translation of numeric flags to string vaules
        """

        retval = ''
        if flags & tcp.TH_FIN != 0:
            retval += 'FIN '
        if flags & tcp.TH_SYN != 0:
            retval += 'SYN '
        if flags & tcp.TH_RST != 0:
            retval += 'RST '
        if flags & tcp.TH_PUSH != 0:
            retval += 'PSH '
        if flags & tcp.TH_ACK != 0:
            retval += 'ACK '
        if flags & tcp.TH_URG != 0:
            retval += 'URG '
        if flags & tcp.TH_ECE != 0:
            retval += 'ECE '
        if flags & tcp.TH_CWR != 0:
            retval += 'CWR '
        return retval

    def has_flag(self, pkt, flag):
        """checks a packet for a given flag
        """

        return pkt.tcp.flags & flag != 0

    def has_flag_simple(self, flags, flag):
        """checks if a given flag is null
        """

        return flags & flag != 0


    def print_tcp_data(self, tcp_data, counter, prefix):
        """deep print tcp data structure
        """
        self.print_debug(
            "%s(%03d)->tcp_data: enc: %s\n%s(%03d)->dec: %s" % (
                prefix,
                counter,
                str(tcp_data['enc']),
                prefix,
                counter,
                str(tcp_data['dec'])
            )
        )

        strrexmit = '%s(%03d)->REXMIT: ' % (prefix, counter)

        for key in tcp_data['rexmit']:
            strrexmit += '{%s : (%s, %s, %+d)}, ' % (
                key - tcp_data['dec']['snd']['iss'],
                tcp_data['rexmit'][key][0] - tcp_data['dec']['rcv']['irs'],
                self.get_flag_string_simple(tcp_data['rexmit'][key][1]),
                tcp_data['rexmit'][key][2] - key
            )

        self.print_debug(strrexmit)
        self.print_debug(
            "%s(%03d)->enc-unachk: %s\n%s(%03d)->remote-special: %s\n%s(%03d)->host-close: %s\tremote-close: %s" % (
                prefix,
                counter,
                str(tcp_data['enc']['unachk']),
                prefix,
                counter,
                str(tcp_data['remote-special']),
                prefix,
                counter,
                tcp_data['host-close'],
                tcp_data['remote-close']
            )
        )


    def print_debug(self, message, is_error=False):
        """Logging/Dumping function, only prints on is_error=True,
        but keeps running queue of debug statements
        """
        try:
            self.log_lock.acquire()
            self.log_glob.put(message)
            if is_error:
                print "ERROR_DUMP()"
                sys.stdout.flush()
                while not self.log_glob.empty():
                    #TODO change this to logfile flush, not stdout
                    print self.log_glob.get()
                    #force flushing due to multi-threaded operation
                    sys.stdout.flush()
                print "END ERROR_DUMP()\n"
                sys.stdout.flush()
            elif self.log_glob.qsize() > 4:
                while self.log_glob.qsize() > 4:
                    self.log_glob.get()
            self.log_lock.release()
        except Queue.Full:
            self.log_lock.release()
        except Queue.Empty:
            self.log_lock.release()
