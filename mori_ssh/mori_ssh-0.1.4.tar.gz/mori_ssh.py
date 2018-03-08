#!/usr/bin/env python

import os
import sys
import yaml
import fcntl
import struct
import termios
import pexpect

MSSH_PATH = os.path.join(os.environ['HOME'], '.mssh')
PROMPT = ['#', '>', '$', pexpect.EOF]


def get_size():
    if 'TIOCGWINSZ' in dir(termios):
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912
    s = struct.pack('HHHH', 0, 0, 0, 0)
    x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
    return struct.unpack('HHHH', x)[0:2]


def common_login(username="root", password="", host="localhost", port="22") -> pexpect.spawn:
    child = pexpect.spawn(f'ssh -p {port} {username}@{host}')
    size = get_size()
    child.setwinsize(size[0], size[1])
    child.logfile_send = None
    child.logfile_read = None
    r = child.expect(['Are you sure you want to continue connecting (yes/no)?', 'password:'])
    if r == 0:
        child.sendline('yes')
        child.expect(['password'])
    child.sendline(password)
    return child


def yit_login(username, password, host):
    child = common_login(username, password, host, '22')
    child.expect([f'{username}@'])
    child.sendline('sudo su')
    child.expect([f'{username}: '])
    child.sendline(password)
    child.expect(PROMPT)
    child.sendline('su yitops')
    child.expect(PROMPT)
    child.sendline('cd')
    return child


def common_scp(username="root", password="", host="localhost", port="22", filename="", upload=False):
    remote = f"{username}@{host}"
    if upload:
        cmd = f"scp -P {port} ./{filename} {remote}:~/"
    else:
        if '/' not in filename:
            cmd = f"scp -P {port} {remote}:~/{filename} {os.getcwd()}/{filename}"
        else:
            raw_file_name = filename.split('/')[-1]
            cmd = f"scp -P {port} {remote}:{filename} {os.getcwd()}/{raw_file_name}"
    print(cmd)
    child = pexpect.spawn(cmd)
    size = get_size()
    child.setwinsize(size[0], size[1])
    r = child.expect(['(yes/no)', 'password:'])
    if r == 0:
        child.sendline('yes')
        child.expect(['password:'])
    child.sendline(password)
    return child


def conf_check():
    confs = {}
    try:
        if os.path.exists(MSSH_PATH) is True:
            for i in os.listdir(MSSH_PATH):
                if '.yaml' in i:
                    f = os.path.join(MSSH_PATH, i)
                    confs.update(yaml.load(open(f, 'r')))
            if len(confs) == 0:
                print('You Didn`t Have Any Config File')
                exit()
            return confs
        else:
            os.mkdir(MSSH_PATH)
            print('Please Put Your Config Yaml File At ~/.mssh/')
            exit()
    except Exception as e:
        print(e)


def main():
    configs = conf_check()
    args = sys.argv[1:]

    if len(args) == 0 or \
            '-h' in args[0] or \
            '--h' in args[0] or \
            '-help' in args[0] or \
            '--help' in args[0]:
        print('mssh {config_name} {file_path (if scp)} -u(if upload)')
        print('eg: mssh xxxx ./test -u (scp upload)')
        print('eg: mssh xxxx test (scp download)')
        print('eg: mssh xxxx (ssh)')
        exit()

    config_name = args.pop(0)
    if config_name not in configs:
        print(f'Please Make Sure Config Name Is In {configs}')
        exit()
    config = configs[config_name]

    if len(args) != 0:
        file_path = args.pop(0)
        if 'yit' in config:
            config.pop('yit')
        if len(args) != 0 and args[0] == '-u':
            expect = common_scp(**config, filename=file_path, upload=True)
        else:
            expect = common_scp(**config, filename=file_path)
        expect.interact()
    else:
        if 'yit' in config:
            config.pop('yit')
            expect = yit_login(**config)
        else:
            expect = common_login(**config)
        expect.interact()


if __name__ == '__main__':
    sys.exit(main())
