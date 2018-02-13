#!/usr/bin/python
import sys
import paramiko
import get_pass
import signal
import time
import select

CONFIG = {}

def print_help():
    print ('*' * 80)
    print (' '*25 + 'Flamingo showlog')
    print ('*' * 80)
    print ('  %-20s\t%-20s\t%s' % ('alias', 'host', 'path'))
    print ('-' * 80)

    for name in sorted(CONFIG.keys()):
        print ('  %-20s\t%-20s\t%s' % (name, CONFIG[name]['host'], CONFIG[name]['path']))
    print ('*' * 80)

    print ('ex)')
    print ('$ python flamingo-cli showlog dev.namenode1')

def view_log(alias):
    info = CONFIG[alias]

    host = info['host']
    user = info['user']
    pw = get_pass.get_pass('%s@%s' % (user, host))

    command = 'tail -f %s' % info['path']

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=pw)
    transport = client.get_transport()
    ch = transport.open_session()
    ch.exec_command(command)

    while True:
        try:
            rl, wl, xl = select.select([ch], [], [], 0.0)
            if len(rl) > 0:
                # Must be stdout
                print (ch.recv(1024))
        except:
            print ('close...')
            client.close()
            return


def signal_handler(signal, frame):
    sys.exit(0)

def main_showlog(argv):
    if len(sys.argv) >= 3:
        alias = sys.argv[2]
        if alias in CONFIG:
            view_log(alias)
        else:
            print_help()
    else:
      print_help()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main_showlog(sys.argv)