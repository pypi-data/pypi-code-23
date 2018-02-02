from lib.user_exception import UserException as Ux


def outerfunc(parm1):
    myfunc(parm1, 'bar')


def myfunc(parm1, parm2):
    my_exception = Ux('throwing a user exception')
    raise my_exception


if __name__ == '__main__':
    try:
        outerfunc('foo')
    except Ux as e:
        print e.text
