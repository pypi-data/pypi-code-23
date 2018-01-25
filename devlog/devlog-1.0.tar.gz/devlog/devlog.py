import sys
import os
import subprocess

import datetime


def devlog():
    arg = sys.argv[1] if sys.argv.__len__() > 1 else None
    if arg is None:
        log()
    elif '-l' == arg:
        save_log(sys.argv[2])
    elif '-h' == arg or '--help' == arg:
        print_help()
    elif 'open' == arg:
        open_directory()
    else:
        print("Type devlog -h or devlog --help to see all commands")


def log():
    lines = ''
    log_m = input('Enter Log: (Leave an empty line to quit and save log)\n> ')
    while log_m != '':
        lines = lines + log_m + '\n'
        log_m = input('> ')
    save_log(lines)


def save_log(m):
    date = datetime.datetime.now()
    day = date.strftime("%d-%m-%Y")
    time = date.strftime("%H:%M")
    file = open(os.path.join(path, 'devlog.md'), "a+")
    file.write('{} {} {}\n'.format(day, time, m))
    file.close()
    print(m)


def list_logs():
    pass


def print_help():
    help_message = 'Devlog is a simple command line tool to help you keep track of'\
                    'progress in your coding journey.\n\n'\
                    'Options:\n\topen\t: Open folder where markdown file is saved' \
                   '\t-l "<Enter your log here>"\t: Log a quick message.\n'\
                    '\t-h or --help\t: Get help and view all commands for devlog'
    print(help_message)


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def open_directory():
    if sys.platform == 'darwin':
        subprocess.check_call(['open', '--', path])
    elif sys.platform == 'linux2':
        subprocess.check_call(['xdg-open', '--', path])
    elif sys.platform == 'win32':
        subprocess.check_call(['explorer', path])


path = os.path.join(os.path.expanduser('~'), 'Documents/Devlog')
check_dir(path)
devlog()
