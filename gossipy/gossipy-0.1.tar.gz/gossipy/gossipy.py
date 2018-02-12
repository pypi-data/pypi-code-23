#!/usr/bin/env python

# A basic chat class in Python 3.

# The MIT License (MIT)
# 
# Copyright (c) 2018 Roberto Reale
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import socket
import threading
import time

class gossipy(object):
        def send(self):
            while True:
                msg = input('\nLOCAL > ')
                if msg and len(msg) > 0:
                    self.sender(msg)

        def receive(self):
            while True:
                msg = self.receiver()
                for m in msg:
                    print('\nREMOTE > ' + m)
                time.sleep(self.delay)

        def start(self):
            thread_send = threading.Thread(target = self.send)
            thread_receive = threading.Thread(target = self.receive)
            thread_send.start()
            thread_receive.start()

        def __init__(self, sender, receiver, delay=1):
            self.sender = sender
            self.receiver = receiver
            self.delay = delay


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
