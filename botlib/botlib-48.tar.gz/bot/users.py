# BOTLIB - Framework to program bots !!
#
# users (users)
#
# Copyright 2017,2018 B.H.J Thate
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice don't have to be included.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.
#
# 9-1-2018 As the creator of this file, I disclaim all rights on this file. 
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" register an user and give them USER , OPER or UBER permission. """

from bot.db import Db
from bot.obj import Object
from bot.utils.misc import stripped


import logging

class User(Object):

    """ User object to store user data. """

    pass

class Users(Db):

    """ Users class providing methods to check/verify/allow users based on origin. """

    _userhosts = Object()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._origins = Object()

    def allowed(self, origin, perm):
        """ check whether a user has a permission. """
        perm = perm.upper()
        user = self.fetch(origin)
        if user and perm in user.perms:
            return True
        user = self.fetch(origin)
        if user and perm in user.perms:
            return True
        logging.error("denied %s %s" % (origin, perm))
        return False

    def delete(self, origin, perm):
        """ add a user to the store. """
        user = self.fetch(origin)
        if user:
            try:
                user.perms.remove(perm)
                user.sync()
            except ValueError:
                pass
        return user

    def fetch(self, origin):
        """ return user data. """
        if origin in self._origins:
            return self._origins[origin]
        userz = list(self.find("user", origin))
        if not userz:
            userz = list(self.find("user", stripped(origin)))
        if userz:
            user = userz[-1]
            if user:
                self._origins[origin] = user
            return user

    def meet(self, origin):
        """ add a user to the store. """
        logging.warn("meet %s" % origin)
        user = self.fetch(origin)
        if not user:
            user = User()
            user.user = origin
            user.origin = origin
            user.perms = ["USER",]
            user.save()
        return user

    def oper(self, origin):
        logging.info("oper %s" % origin)
        opers = self.fetch(origin)
        if not opers:
            user = User()
            user.user = origin
            user.perms = ["OPER", "USER"]
            user.save()
            return user

    def perm(self, origin, perm):
        """ set a permission of a user. """
        logging.warn("perm %s %s" % (origin, perm))
        user = self.fetch(origin)
        if user:
            if perm.upper() not in user.perms:
                user.perms.append(perm.upper())
                user.sync()
        return user

    def uber(self, origin):
        """ add a user to the store. """
        logging.info("uber %s" % origin)
        opers = self.fetch(origin)
        if not opers:
            user = User()
            user.user = origin
            user.perms = ["UBER", "OPER", "USER"]
            user.save()
            return user
