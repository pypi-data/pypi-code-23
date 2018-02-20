#!/usr/bin/env python3
import sys
import traceback
import subprocess
import argparse
import os
import os.path
import hashlib
import binascii
import urllib
import json

import appdirs as _appdirs
import psutil
from trezorlib.client import TrezorClient
import trezorlib.messages as trezor_proto
from trezorlib.device import TrezorDevice

debug = os.environ.get('PINENTRY_TREZOR_DEBUG') == '1'
dontflash = os.environ.get('PINENTRY_TREZOR_DONT_FLASH') == '1'
conf_keyset = os.environ.get('PINENTRY_TREZOR_KEYSET')

appdirs = _appdirs.AppDirs('trezor_gpg', 'zarbosoft')
metadir = appdirs.user_cache_dir
keylookupdir = os.path.join(metadir, 'keylookup')


_log = None


def resp(text):
    print(text)
    try:
        sys.stdout.flush()
    except BrokenPipeError:
        pass


def log(text):
    if not _log:
        return
    _log.write(text + '\n')
    _log.flush()


def log_e():
    if not _log:
        return
    traceback.print_exc(file=_log)
    _log.write('\n')
    _log.flush()


def lookup_key(grip=None, key=None):
    pinsource = None
    found = False
    for line in subprocess.check_output([
                'gpg2',
                '--with-keygrip', '--with-colons',
                '--list-secret-keys'
            ]).decode('utf-8').splitlines():
        cols = line.split(':')
        log('GPG keys cols {}'.format(cols))
        if cols[0] == 'fpr':
            if found:
                break
            pinsource = cols[9].lower()
        elif cols[0] == 'grp' and cols[9].lower() == grip:
            found = True
        elif cols[0] == 'uid':
            if key and key in cols[9]:
                found = True
    if found:
        return pinsource
    else:
        return None


def tk_entry(pinsource, message, error):
    import tkinter as tk

    while True:
        devices = TrezorDevice.enumerate()
        if devices:
            break

        root = tk.Tk()
        error_out = []

        def do_cancel():
            error_out.append(RuntimeError('User aborted input'))
            root.destroy()

        frame = tk.Frame(root)
        frame.pack()
        tk.Label(
            frame,
            text='Could not locate Trezor, please make sure it\'s connected.',
            wraplength='10cm',
            justify='left',
        ).pack()
        actions = tk.Frame(frame)
        tk.Button(
            actions, text='Retry', command=root.destroy
        ).pack(side='left')
        tk.Button(
            actions, text='Cancel', command=do_cancel
        ).pack(side='right')
        actions.pack(padx=3, pady=3)
        tk.mainloop()
        if error_out:
            raise error_out[0]

    while True:
        try:
            device = devices[0]
            break
        except Exception as e:
            root = tk.Tk()
            error_out = []

            def do_cancel():
                error_out.append(RuntimeError('User aborted input'))
                root.destroy()

            frame = tk.Frame(root)
            frame.pack()
            tk.Label(
                frame,
                text='Could not open Trezor, please make sure your '
                'permissions correct and it is still connected. '
                'Error: {}'
                ''.format(str(e)),
                wraplength='10cm',
                justify='left',
            ).pack()
            actions = tk.Frame(frame)
            tk.Button(
                actions, text='Retry', command=root.destroy
            ).pack(side='left')
            tk.Button(
                actions, text='Cancel', command=do_cancel
            ).pack(side='right')
            actions.pack()
            tk.mainloop()
            if error_out:
                raise error_out[0]

    class MyClient(TrezorClient):
        def __init__(self):
            super().__init__(device)

        def callback_PinMatrixRequest(self, msg):
            try:
                return self._pinentry(msg)
            except:  # noqa
                log_e()
                self.cancel()

        def _pinentry(self, msg):
            root = tk.Tk()

            pin = []

            def do_clear(*pargs, **kwargs):
                del pin[:]

                if not dontflash:
                    button = buttons['clear']
                    button.configure(text='*Clear*')

                    def reset():
                        button.configure(text='Clear')

                    button.after(100, reset)

            _done = []

            def done(*pargs, **kwargs):
                _done.append(True)
                root.destroy()

            root.bind('<Return>', done)
            root.bind('<Escape>', lambda *p, **k: root.destroy())
            root.bind('<BackSpace>', do_clear)

            buttons = {}

            def entry(value):
                pin.append(value)

                if not dontflash:
                    button = buttons[value]
                    button.configure(text='X')

                    def reset():
                        button.configure(text=' ')

                    button.after(100, reset)

            for keyset in (
                    ['123456789'] +
                    ([conf_keyset] if conf_keyset
                        else ['xcvsdfwer', 'm,.jkluio'])
                    ):
                for k, i in zip(keyset, '123456789'):
                    root.bind(k, lambda e, i=i: entry(i))

            frame = tk.Frame(root)
            frame.pack()
            tk.Label(
                frame,
                text=message,
                wraplength='10cm',
                justify='left',
            ).pack()
            if error:
                tk.Label(
                    frame,
                    text=error,
                    fg='red',
                    wraplength='10cm',
                    justify='left',
                ).pack()

            buttons_frame = tk.Frame(frame)
            for i, v in enumerate('789456123'):
                button = tk.Button(
                    buttons_frame,
                    text=' ',
                    width=3,
                    height=3,
                    command=lambda v=v: entry(v),
                )
                buttons[v] = button
                button.grid(
                    row=int(i / 3),
                    column=i % 3,
                    padx=3,
                    pady=3,
                )
            buttons_frame.pack()

            actions = tk.Frame(frame)
            tk.Button(
                actions, text='Done', command=done
            ).pack(side='right')
            buttons['clear'] = tk.Button(
                actions, text='Clear', command=do_clear
            )
            buttons['clear'].pack(side='right')
            tk.Button(
                actions, text='Cancel', command=root.destroy
            ).pack(side='right')
            actions.pack(padx=3, pady=3)

            tk.mainloop()
            if not _done:
                raise RuntimeError('Canceled by user')

            return trezor_proto.PinMatrixAck(pin=''.join(pin))

    client = MyClient()

    bip32_path = [10, 0]  # not quite sure what this is
    return binascii.hexlify(client.decrypt_keyvalue(
        bip32_path,
        'GPG: ' + pinsource,  # this needs to be stable
        hashlib.sha256(binascii.unhexlify(pinsource)).digest()
    ))


def as_pinentry():
    try:
        resp('OK')
        pinsource = None
        message = ''
        error = ''
        opmode = 'unlock'
        pinmode = 'unlock'
        for line in sys.stdin:
            splits = line.split(' ', 1)
            command = splits.pop(0).strip()
            rest = splits.pop(0).strip() if splits else None
            log('Command [{}] rest [{}]'.format(command, rest))
            if not command or command in (
                        'SETPROMPT',
                        'SETQUALITYBAR',
                        'SETQUALITYBAR_TT',
                        'SETREPEATERROR',
                        'SETREPEAT',
                        'SETOK',
                        'SETCANCEL',
                    ):
                pass
            elif command == 'SETDESC':
                message = urllib.parse.unquote(rest)
                if 'Please enter the new passphrase' in message:
                    pinmode = 'new'
                elif 'Please re-enter this passphrase' in message:
                    pinmode = 'confirm'
            elif command == 'SETERROR':
                error = rest
            elif command == 'OPTION':
                if rest.startswith('ttyname='):
                    tty = rest.split('=', 1)[-1]  # noqa
                elif rest.startswith('owner='):
                    pid, owner = rest.split('=', 1)[-1].split(' ')
                    at = psutil.Process(int(pid))
                    while at and at.name() != 'trezor_gpg':
                        at = at.parent()
                    if at:
                        try:
                            with open(os.path.join(
                                    keylookupdir, str(at.pid)
                                    )) as keylookup:
                                opmode, key = json.load(keylookup)
                            pinsource = lookup_key(key=key)
                        except FileNotFoundError:
                            pass
            elif command == 'GETINFO':
                pass
            elif command == 'SETKEYINFO':
                if not pinsource and rest and rest.startswith(('n/', 's/')):
                    key, grip = rest.split('/', 1)
                    log('Key info [{}] [{}]'.format(key, grip))
                    pinsource = lookup_key(grip=grip.lower())
            elif command == 'GETPIN':
                if not pinsource:
                    raise RuntimeError(
                        'Never received SETKEYINFO - no pin source for key')
                log('Pin source: {}'.format(pinsource))
                log('opmode [{}] pinmode [{}]'.format(opmode, pinmode))
                if opmode == 'add' and pinmode == 'unlock':
                    decrypted = ''
                elif opmode == 'remove' and pinmode in ('new', 'confirm'):
                    decrypted = ''
                else:
                    # TODO tty input option;
                    # getpass hardcodes tty, need to reinvent wheel again
                    decrypted = tk_entry(
                        pinsource,
                        message,
                        error
                    )
                resp('D {}'.format(decrypted))

                error = ''
            elif command == 'CONFIRM':
                pass
            elif command == 'BYE':
                pass
            else:
                raise RuntimeError('Unknown command [{}] args [{}]'.format(
                    command, rest))
            resp('OK')
    except:  # noqa
        log_e()


def as_setpassphrase(key):
    pinsource = lookup_key(key=key)
    if not pinsource:
        raise RuntimeError('Could not identify key {}'.format(key))
    keylookup_path = os.path.join(keylookupdir, str(os.getpid()))
    os.makedirs(keylookupdir, exist_ok=True)
    try:
        with open(keylookup_path, 'w') as keylookup:
            json.dump(['add', key], keylookup)
        subprocess.check_call(['gpg2', '--passwd', key])
    finally:
        os.unlink(keylookup_path)


def as_removepassphrase(key):
    pinsource = lookup_key(key=key)
    if not pinsource:
        raise RuntimeError('Could not identify key {}'.format(key))
    keylookup_path = os.path.join(keylookupdir, str(os.getpid()))
    os.makedirs(keylookupdir, exist_ok=True)
    try:
        with open(keylookup_path, 'w') as keylookup:
            json.dump(['remove', key], keylookup)
        subprocess.check_call(['gpg2', '--passwd', key])
    finally:
        os.unlink(keylookup_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--display', help='Override X11 display')
    parser.add_argument(
        '-a', '--add', help='Add passphrase on key')
    parser.add_argument(
        '-r', '--remove', help='Remove Trezor passphrase on key')
    args = parser.parse_args()
    if args.display:
        os.environ['DISPLAY'] = args.display

    debug = True
    if debug:
        os.makedirs(appdirs.user_log_dir, exist_ok=True)
        global _log
        _log = open(os.path.join(appdirs.user_log_dir, 'debug.txt'), 'w')
    if args.add:
        as_setpassphrase(args.add)
    elif args.remove:
        as_removepassphrase(args.remove)
    else:
        as_pinentry()


if __name__ == '__main__':
    main()
