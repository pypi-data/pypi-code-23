"""

simcli
~~~~~~


SimpleCli class implementation which can be used to make CLI based utilities.
Author: Denis Khodus aka "Reagent"
License: MIT

"""

import sys
import readline
import os.path


ERR_OK = 0
ERR_UNKONWN = 1
ERR_FAILED = 2
ERR_INVALID_SYNTAX = 3
ERR_MSG = {
    ERR_UNKONWN: "unknown error",
    ERR_FAILED: "operation failed",
    ERR_INVALID_SYNTAX: "invalid syntax",
}


class SimpleCli(object):
    HELP_ROOT = ""
    CLI = {}

    def __init__(self):
        self.prompt = "(\033[1msimcli\033[0m)#"
        self.history = os.path.join(os.path.expanduser('~'), '.simcli_history')
        self.store_history = True
        self._clidef = {}
        self._init_clidef()

    def _init_clidef(self):
        """ Analysing CLI struct definition and defines minimum command length which is enough for every
        entry in the CLI to uniquelly understand which command or operation about to be used. """
        self._clidef = {}
        for cmd in self.CLI:
            cmd_min_len = 1
            is_unique = None
            while is_unique is not True:
                is_unique = True
                for cmd_ in self.CLI:
                    if cmd_ == cmd:
                        continue
                    if cmd_[:cmd_min_len] != cmd[:cmd_min_len]:
                        continue
                    is_unique = False
                    cmd_min_len += 1
                    break
            cmd_op_ = {}
            for op in self.CLI[cmd]:
                op_min_len = 1
                is_unique = None
                while is_unique is not True:
                    is_unique = True
                    for op_ in self.CLI[cmd]:
                        if op_ == op:
                            continue
                        if not op_[:op_min_len] == op[:op_min_len]:
                            continue
                        is_unique = False
                        op_min_len += 1
                        break
                cmd_op_[(op, op_min_len)] = self.CLI[cmd][op]
            self._clidef[(cmd, cmd_min_len)] = cmd_op_

    def _input(self, caption=""):
        readline.set_completer(self._readline_completion)
        if sys.version_info[0] == 2:
            value = raw_input(caption)
        else:
            value = input(caption)
        readline.set_completer(self._readline_complition_disabled)
        if self.store_history:
            try:
                readline.write_history_file(self.history)
            except IOError:
                pass
        return value

    def _input_val(self, caption=""):
        readline.set_completer(self._readline_complition_disabled)
        if sys.version_info[0] == 2:
            value = raw_input(caption)
        else:
            value = input(caption)
        readline.set_completer(self._readline_completion)
        if readline.get_current_history_length() > 0:
            readline.remove_history_item(readline.get_current_history_length() - 1)
        return value

    @staticmethod
    def _ifcli(rq, cmd, min_len=3):
        """ Testing given typed by user request against given command and minimum
        requeried command's characters length. For example, if we have command
        'show' and know that there is no other command which starts with first
        two letters 'sh' - we can give the user opportunity to enter only 'sh',
        or 'sho', or full command 'show': _ifcli(rq, 'show', 2)
        :rq                         User's request he/she typed in;
        :cmd                        Full command;
        :min_len                    Minimum length enough to understand the
                                    command;
        :returns                    True if request is matching the command,
                                    False otherwise.
        """
        if not isinstance(cmd, str) or not isinstance(rq, str):
            return False
        if len(rq) < min_len or len(rq) > len(cmd):
            return False
        return rq == cmd[:len(rq)]

    def _get_clidef(self, *args):
        """
        :*args                      Command and operator (if any typed by the user)
        :returns                    Corresponding CLI definition struct for the given
                                    command and operator; False if nothing found.
        """
        cmd = args[0] if len(args) >= 1 else 'help'
        op = args[1] if len(args) >= 2 else None
        for cmd_ in self._clidef:
            if not self._ifcli(cmd, cmd_[0], cmd_[1]):
                continue
            if self.CLI[cmd_[0]].get('_noop', False):
                return tuple(tuple(self.CLI[cmd_[0]]['_default']) + (cmd_[0], None))
            if op is None and '_default' in self.CLI[cmd_[0]]:
                return tuple(tuple(self.CLI[cmd_[0]]['_default']) + (cmd_[0], None))
            elif op is None:
                op = 'help'
            for op_ in self._clidef[cmd_]:
                if not self._ifcli(op, op_[0], op_[1]):
                    continue
                return tuple(tuple(self._clidef[cmd_][op_]) + (cmd_[0], op_[0]))
        return False

    @staticmethod
    def _readline_complition_disabled(text, state):
        """ Internal completion method used with 'readline' """
        return None

    def _readline_completion(self, text, state):
        """ Internal completion method used with 'readline' """
        if not text:
            sys.stdout.write(self.HELP_ROOT)
            sys.stdout.write("\n%s " % self.prompt)
            return None
        parts = text.split(" ")
        if not parts[-1]:
            parts = parts[:-1]

        cmd = parts[0] if len(parts) >= 1 else 'help'
        op = parts[1] if len(parts) >= 2 else 'help'
        clidef = self._get_clidef(cmd, op)
        if clidef is not False:
            helpmsg = clidef[1]
            if not helpmsg.startswith('\n'):
                helpmsg = "\n" + helpmsg
            print(helpmsg)
            sys.stdout.write("\n%s %s" % (self.prompt, text))
            return None
        return None

    def _print_err(self, errcode=ERR_UNKONWN, errmsg=None, extra_cr=True):
        """ Prints error code and its defition, if any given or exists in the pre-defined
        error constants. Also prints 'OK' with success message if given.
        :errcode                    Integer containing the error code (errcode=0 means OK);
        :errmsg                     A custom error message; if not set - method will try to
                                    find corresponding error message in the ERR_MSG
                                    constant.
        :extra_cr                   If set to True - prints an addiditonal line return (CR)
                                    after error message.
        """
        if errcode == 0:
            sys.stdout.write("\033[1m\033[92m[OK]\033[0m")
            if errmsg:
                sys.stdout.write(" %s" % errmsg)
            sys.stdout.write("\n")
        elif errcode != -1:
            sys.stdout.write("\033[1m\033[91mERROR(%i)\033[0m" % errcode)
            if not errmsg and errcode in ERR_MSG:
                errmsg = ERR_MSG[errcode]
            if errmsg:
                sys.stdout.write(": %s" % errmsg)
            sys.stdout.write("\n")
        if extra_cr:
            sys.stdout.write("\n")

    def _validaterq(self, method_name, helpmsg, cmd, op, *args):
        """ Optional method used to validate request given by end user; always returns
        True for base class (SimpleCli class) meaning 'Request is OK', and can be
        overriden by end class using this one to make CLI to verify something before
        found method called.
        :returns                    True if request can be continued, False to abort.
        """
        return True

    def start(self):
        """ The entry point for the CLI """
        try:
            readline.read_history_file(self.history)
        except IOError:
            pass
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('?: complete')
        readline.set_completer(self._readline_completion)
        readline.set_completer_delims("\n")
        do_exit = False
        while not do_exit:
            rq = self._input("%s " % self.prompt).strip()
            if rq == '':
                continue
            if self._ifcli(rq, 'exit', 2) or self._ifcli(rq, 'quit', 1):
                do_exit = True
                continue
            rq = rq.strip().split(" ") if rq.strip() else []
            cmd = rq[0] if len(rq) >= 1 else None
            op = rq[1] if len(rq) >= 2 else None
            params = rq[2:] if len(rq) >= 3 else []
            clidef = self._get_clidef(cmd, op)
            if clidef is False:
                print("command not supported\n")
                continue
            method_name, helpmsg, cmd, op = clidef
            if op is None and len(rq) >= 2:
                params.insert(0, rq[1])
            if not self._validaterq(method_name, helpmsg, cmd, op, *params):
                continue
            method = getattr(self, method_name, False)
            if method is False:
                print("command not implemented yet\n")
                continue
            result = method(cmd, op, *params)
            if isinstance(result, (tuple, list)) and len(result) == 2:
                errcode, errmsg = result
            elif isinstance(result, int):
                errcode, errmsg = result, False
            elif result is False:
                errcode, errmsg = 1, False
            elif result is True:
                errcode, errmsg = 0, False
            else:
                errcode, errmsg = -1, False
            self._print_err(errcode, errmsg)

    def cli_help(self, *args):
        """ Prints help for the command """
        if not args or args[0] == 'help':
            print(self.HELP_ROOT)
            return
        cmd = args[0]
        if cmd not in self.CLI:
            print("There is no help page for this command defined\n")
            return
        helpmsg = self.CLI[cmd].get('help', False)
        if not helpmsg:
            print("There is no help page for this command defined\n")
            return
        helpmsg = helpmsg[1]
        if not helpmsg.startswith('\n'):
            helpmsg = "\n" + helpmsg
        print(helpmsg)
        return

