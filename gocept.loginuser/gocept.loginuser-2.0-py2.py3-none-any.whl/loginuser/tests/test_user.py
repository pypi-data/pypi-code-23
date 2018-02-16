# encoding=utf-8
import gocept.loginuser.user


def test_user__User__check_password_1():
    """`User.check_password()` verifies a password."""
    user = gocept.loginuser.user.User()
    user.password = 'asdf'
    assert user.check_password('asdf')
    assert not user.check_password('bsdf')
