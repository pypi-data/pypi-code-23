import inspect


class UserException(Exception):
    def __init__(self, msg='user exception', sp=True):
        self.msg = msg
        self.message = msg
        if sp:
            self.text = stat_prefix(2) + ' - ' + msg
        else:
            self.text = msg

    def __str__(self):
        return self.text

    def get_msg(self):
        return self.msg


class UserFailException(UserException):
    def __init__(self, msg='fail exception'):
        UserException.__init__(self, msg, False)


class UserTimeoutException(UserException):
    def __init__(self, msg='timeout exception'):
        UserException.__init__(self, msg, False)


def stat_prefix(splevel=2):
    fr = inspect.currentframe()
    for i in range(splevel):
        fr = fr.f_back
    fc = fr.f_code
    args = fc.co_varnames[1:fc.co_argcount]
    argvals = [repr(fr.f_locals[arg]) for arg in args]
    arglist = ', '.join(argvals)
    return '[%s:%s] %s(%s)' % (fc.co_filename, fr.f_lineno, fc.co_name, arglist)
