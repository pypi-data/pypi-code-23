#!/usr/bin/python
import sys
import signal
import socket

CONFIG = {}

def print_help():
    print ('*' * 80)
    print (' '*25 + 'Flamingo status')
    print ('*' * 80)
    print ('  %-20s\t%s:%s' % ('alias', 'host', 'port'))
    print ('-' * 80)

    for name in sorted(CONFIG.keys()):
        print ('  %-20s\t%s:%s' % (name, CONFIG[name]['host'], CONFIG[name]['port']))
    print ('*' * 80)

    print ('ex)')
    print ('$ python cli.py status dev.web')
    print ('$ python cli.py status-all')

def status(alias):
    info = CONFIG[alias]

    host = info['host']
    port = info['port']

    result, cause = test_port_scan(host, port)

    if result:
        print ('[%s] %-25s %s' % ('OK', alias, host+':'+port))
    else:
        print ('[%s] %-25s %s (%s)' % ('Fail', alias, host+':'+port, cause))

# import subprocess
# ping_result = {}
# def test_ping(host):
#     if host in ping_result:
#         result = ping_result[host]
#     else:
#         result = subprocess.Popen(['ping', '-c', '1','-t', '1', host], stdout=subprocess.PIPE).stdout.read()
#         # result = os.system('ping -c 1 -t 1 %s' % host)
#
#     ping_result[host] = result
#
#     return result == 0

def test_port_scan(host, port):
    result = False
    cause = ''
    sock = None

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        errorno = sock.connect_ex((host, int(port)))
        sock.send ('test'.encode())

        if errorno == 0:
            result = True

        else:
            result = False

        sock.close()

    except KeyboardInterrupt:
        cause = "You pressed Ctrl+C"
        if sock is not None: sock.close()

    except socket.gaierror:
        cause = 'Hostname could not be resolved. Exiting'
        if sock is not None: sock.close()

    except socket.error:
        cause = "Couldn't connect to server"
        if sock is not None: sock.close()

    return result, cause

def signal_handler(signal, frame):
    sys.exit(0)

def main_status(argv):
    # python ssh.py arg1 arg2 -> ['ssh.py', 'arg1', 'arg2']

    if len(argv) >= 2:
        alias = argv[1]

        if alias in CONFIG:
            status(alias)
        else:
            print_help()
    else:
      print_help()

def main_status_all(argv):
    for s in sorted(CONFIG):
        status(s)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main_status(sys.argv)