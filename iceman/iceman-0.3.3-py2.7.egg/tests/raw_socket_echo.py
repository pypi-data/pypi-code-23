#!/usr/bin/env python

import socket
import argparse
import sys
import struct

from timeit import default_timer as timer
from time import sleep

from contextlib import closing #since socket in 2.7 is not a context manager

def transmit(args):
    try:
        typeValue = typeValues[0] if args.type == typeChoices[0] else typeValues[1]

        print "CLIENT: Connecting to %s:%s" % (args.hostname,args.port)
        with closing(socket.create_connection((args.hostname,args.port))) as skt:
            print "CLIENT: Connecting from %s:%s" % (skt.getsockname()[0], skt.getsockname()[1])
            skt.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            #check socket options
            sz_snd_buf = skt.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            sz_rcv_buf = skt.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            print "CLIENT: SND Buffer: %d and RCV Buffer: %s" % (sz_snd_buf, sz_rcv_buf)

            #create test message
            msg_old = "TEST CODE MESSAGE, WAIT FOR RESPONSE"
            msg_old_len = len(msg_old)

            #repeat string out to specified length
            msg = (msg_old * ((args.length/len(msg_old))+1))[:args.length]
            data_expected = len(msg)

            print "CLIENT: Sending header"
            packed_len = struct.pack('I', data_expected)
            skt.sendall(packed_len)

            echo_total = 0
            echo_counter = 0
            echo_total_start = 0
            marker = args.marker # 1MB
            
            #loop continuously
            echo_start = timer()
            while True:
                data_all = ''
                data_rcvd = 0
                #TODO add watchdog timer to send and recv calls to terminate and print relevant debug info (3-5 second timeout)
                if typeValue == 0:
                    #loop sending data until it fails
                    fault = None
                    while fault == None:
                        fault = skt.sendall(msg)
                        # sleep(0.02)
                    print "CLIENT: skt.sendall faulted out: %s" % fault
                else:
                    skt.sendall(msg)

                    while data_rcvd < data_expected:
                        data = skt.recv(data_expected - data_rcvd)
                        data_rcvd += len(data)
                        if not data:
                            print "CLIENT: Received partial: %d bytes of %d using: %s" % (
                                data_rcvd, 
                                data_expected, 
                                "{:,}".format(data_expected)
                            )
                            break
                        else:
                            data_all += data
                    #validate echo string
                    if data_all != msg:
                        print "CLIENT: msg did NOT validate, using %s" % "{:,}".format(data_expected)
                    
                    echo_total += data_expected
                    if echo_total > marker:
                        echo_stop = timer() - echo_start
                        echo_start = timer()
                        print "CLIENT: Echoed %s bytes, SEND Buffer: %s, SPEED: ~%s bps" % (
                            "{:,}".format(echo_counter * marker + echo_total), 
                            "{:,}".format(data_expected),
                            #multiply by 2 since the data is travelling roundtrip and it's both upload and download together...
                            "{:,}".format(round(2*8*(echo_total - echo_total_start)/(echo_stop)))
                        )
                        echo_total = echo_total % marker
                        echo_total_start = echo_total
                        echo_counter += 1
                    #increment size of message if requested
                    if args.increment > 0:
                        data_expected += args.increment
                        msg = (msg_old * (((data_expected)/len(msg_old))+1))[:data_expected]
    except Exception, ex:
        print "CLIENT: Error occurred, %s" % str(ex)
    except KeyboardInterrupt:
        print "CLIENT: Ctrl-C Recvd, exiting"
    return

def listen(args):
    try:
        typeValue = typeValues[0] if args.type == typeChoices[0] else typeValues[1]

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as skt:
            #set socket options, may need to vary this some
            skt.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)   #disable nagle's algorithm for handling RTT
            skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #reuse address if already in use
            
            #check socket options
            sz_snd_buf = skt.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            sz_rcv_buf = skt.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            print "SVR: SND Buffer: %d and RCV Buffer: %s" % (sz_snd_buf, sz_rcv_buf)

            skt.bind((args.hostname,args.port))
            
            #listen and allow only 1 queued connection
            skt.listen(1)
            print "SVR: Listening on %s:%s" % (args.hostname, args.port)
            
            #wait for a client to connect
            conn, client_addr = skt.accept()
            print "SVR: Connected to %s" % str(client_addr)

            #get the 4 byte length header
            data = ''
            while len(data) < 4:
                data += conn.recv(4)
            data_expected = int(struct.unpack('I', data)[0])
            print "SVR: Expecting %s bytes" % data_expected

            recv_total = 0
            recv_counter = 0
            recv_total_start = 0
            marker = args.marker # 1MB

            recv_start = timer()
            no_fault = True
            #continue to transfer until something goes wrong
            while no_fault:
                data_rcvd = 0
                data_all = ''
                #download one whole segment of data and then echo it
                while data_rcvd < data_expected:
                    data = conn.recv(data_expected - data_rcvd)
                    if data:
                        #only echo if that's the current mode
                        if typeValue == 1:
                            conn.sendall(data)
                        data_rcvd += len(data)
                        data_all += data
                        
                    #if nothing was received at all, fault out
                    elif data_all == '':
                        no_fault = False
                        break
                    else:
                        #received a partial segment and then nothing, odd
                        print "SVR: Received partial: %d bytes of %d" % (data_rcvd, data_expected)
                        break
                #validate message
                msgcmp = "TEST CODE MESSAGE, WAIT FOR RESPONSE"
                msgcmp = (msgcmp * ((data_rcvd/len(msgcmp))+1))[:data_rcvd]
                if msgcmp != data_all:
                    print "SVR: Comparison Failed using %s" % (
                        "{:,}".format(data_expected)
                        # data_all, 
                        # msgcmp
                    )
                #increment the window if specified
                if args.increment > 0:
                    data_expected += args.increment
                #print byte stats if not echoing
                if typeValue == 0:
                    recv_total += data_expected
                    if recv_total > marker:
                        recv_stop = timer() - recv_start
                        recv_start = timer()
                        print "SVR: Recv'd %s bytes, SEND Buffer: %s, SPEED: ~%s bps" % (
                            "{:,}".format(recv_counter * marker + recv_total), 
                            "{:,}".format(data_expected),
                            "{:,}".format(round(8*(recv_total - recv_total_start)/(recv_stop)))
                        )
                        recv_total = recv_total % marker
                        recv_total_start = recv_total
                        recv_counter += 1
            print "SVR: Done Processing"
    except KeyboardInterrupt:
        print "SVR: Ctrl-C Recvd, exiting"
    return

#choices for program type
typeChoices = ['oneway', 'echo',]
#typeChoices conversion to simple ints for easy checks
typeValues = [0, 1]

def main():
    """main entrypoint
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='0.0.1')
    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default='80')
    parser.add_argument('-n',
                        '--hostname',
                        default='127.0.0.1')
    parser.add_argument('-i',
                        '--increment',
                        type=int,
                        default=0)
    parser.add_argument('-t',
                        '--type',
                        choices=typeChoices,
                        default='oneway')
    parser.add_argument('-m',
                                '--marker',
                                type=int,
                                default=1000000) #default to 1MB marker prints

    subparsers = parser.add_subparsers(help='commands')

    server_parser = subparsers.add_parser('server')
    server_parser.set_defaults(func=listen)

    client_parser = subparsers.add_parser('client')
    client_parser.add_argument('-l',
                                  '--length',
                                  type=int,
                                  required=True)
                                  
    client_parser.set_defaults(func=transmit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
