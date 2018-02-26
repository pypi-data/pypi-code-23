#!/usr/bin/env python

import sys, os

DEFAULT_SERVER = '116.62.229.195'
DEFAULT_PORT = 2000

def print_usage():
    print "Usage: {0} terminal/client [-s xxx.xxx.xx.xx] [-p xxxxx]\n".format(sys.argv[0])

def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    host_name = DEFAULT_SERVER
    host_port = DEFAULT_PORT

    mode = sys.argv[1]
    i = 2; arg_num = len(sys.argv)
    while i < arg_num:
        if sys.argv[i] == '-s' and (i+1) < arg_num:
            host_name = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == '-p' and (i+1) < arg_num:
            try:
                host_port = int(sys.argv[i+1])
            except:
                print "error: valid port '{0}'".format(sys.argv[i+1])
                sys.exit(1)
            i += 1
        else:
            print "error: invalid argument '{0}'".format(' '.join(sys.argv[1:]))
            print_usage()
            sys.exit(1)
        i += 1

    if os.name == 'posix':
        tmpfile_folder = '/tmp/'
    elif os.name == 'nt':
        tmpfile_folder = os.path.expanduser('~') + '\\'

    if mode == "client":
        from client import Client
        if host_name == None:
            print_usage()
            sys.exit(1)

        tmpfile = tmpfile_folder + '.testbed_client'
        if os.path.exists(tmpfile):
            print "An udevice center client is already running"
            sys.exit(1)

        open(tmpfile, 'a').close()
        client = Client()
        client.client_func(host_name, host_port)
        os.remove(tmpfile)
    elif mode == "terminal":
        from terminal import Terminal
        if host_name == None:
            print_usage()
            sys.exit(1)
        terminal = Terminal()
        terminal.terminal_func(host_name, host_port)
    else:
        print_usage()
    sys.exit(0)

if __name__ == '__main__':
    main()
