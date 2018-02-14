#!/usr/bin/python

from random import *
import string
import random

class Hostname:
    def set(self, choice):
        current = self.current()
        self.output(current, choice)
        self.change(choice)

    def output(self, current, choice):
        print('Current hostname: ' + current)
        print('New hostname: ' + choice)

    def rand(self):
        char = string.ascii_lowercase
        length = randint(2, 8)
        return ('' . join((random.choice(char)) for x in range(length)))

    def current(self):
        return open('/etc/hostname', 'r').read()

    def change(self, text):
        f = open("/etc/hostname", mode="w")
        f.write(text)
        f.close()
