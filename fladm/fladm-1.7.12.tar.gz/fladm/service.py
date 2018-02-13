#!/usr/bin/python
import sys
import paramiko
import get_pass
import signal
import time

CONFIG = {}

def print_help():
    print ('*' * 80)
    print (' '*25 + 'Flamingo service')
    print ('*' * 80)
    print ('  %-20s\t%-20s\t%s' % ('alias', 'host', 'path'))
    print ('-' * 80)

    for name in sorted(CONFIG.keys()):
        print ('  %-20s\t%-20s\t%s' % (name, CONFIG[name]['host'], CONFIG[name]['path']))
    print ('*' * 80)

    print ('ex)')
    print ('$ python cli.py dev.zeppelin [start|stop|restart]')

def service(alias, op):
    info = CONFIG[alias]

    host = info['host']
    user = info['user']

    if 'password' in info:
        pw = info['password']
    else:
        pw = get_pass.get_pass('%s@%s' % (user, host))

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=pw)

    if type(info[op]) is list:
        commands = info[op]
    else:
        commands = [info[op]]

    commands.insert(0, "cd %s" % info['path'])

    ch = ssh.invoke_shell()
    out = ch.recv(9999)
    print (out)

    try:
        for cmd in commands:
            command = '%s \n' % (cmd)
            # print ("> %s" % command)
            ch.send(command)
            out = ''

            # wait for complete
            while not "#" in out:
                while not ch.recv_ready():
                    time.sleep(0.1)

                out = ch.recv(9999)
                print out,

                time.sleep(0.1)
    finally:
        ssh.close()

def signal_handler(signal, frame):
    sys.exit(0)

def main_service(argv):
    if len(argv) >= 3:
        alias = argv[1]
        op = argv[2]
        if alias in CONFIG:
            service(alias, op)
        else:
            print_help()
    else:
      print_help()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main_service(sys.argv)