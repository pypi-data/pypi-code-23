#!/usr/bin/python

class Completer:
    data = []

    def get(self, text, state):
        options = [x for x in self.data if x.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None
