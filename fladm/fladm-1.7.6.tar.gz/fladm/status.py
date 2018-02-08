#!/usr/bin/python
import sys
import signal
import socket
import requests
import json
import argparse

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

def get_status(alias):
    result_obj = {}
    info = CONFIG[alias]

    host = info['host']
    port = info['port']

    result, cause = test_port_scan(host, port)

    result_obj['result'] = result
    result_obj['cause'] = cause
    result_obj['alias'] = alias
    result_obj['host'] = host
    result_obj['port'] = port

    return result_obj

def status(alias):
    result = get_status(alias)

    if result['result']:
        print ('[%s] %-25s %s' % ('OK', result['alias'], result['host']+':'+result['port']))
    else:
        print ('[%s] %-25s %s (%s)' % ('Fail', result['alias'], result['host']+':'+result['port'], result['cause']))

    return result

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

def send_message_slack(webhookurl, channel, title, message, color):
    payload = {
        'channel': channel,
        'text': title,
        'attachments': [{
            'text': message,
            'color': color
        }]
    }

    url = webhookurl
    data = 'payload=%s' % json.dumps(payload)
    r = requests.post(url=url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    print (r)

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


def status_all(argv):
    statuses = []

    for s in sorted(CONFIG):
        statuses.append(status(s))

    if 'channel' in argv and 'webhookurl' in argv:
        message = ''

        for s in statuses:
            if s['result'] == False:
                message += '%s \t%s:%s failed!\n' % (s['alias'], s['host'], s['port'])

        if message:
            send_message_slack(argv.webhookurl, argv.channel, 'Flamingo health alert', message, '#ff0000')


def main_status_all(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-channel', help="Slack channel", required=False)
    parser.add_argument('-webhookurl', help="Slack Webhookurl", required=False)
    parser.set_defaults(func=status_all)
    args = parser.parse_args(sys.argv[2:])
    args.func(args)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main_status(sys.argv)