#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class IronpipeRun(object):
    def __init__(self, run):
        self.run = run

    def __repr__(self):
        return self.run['id']

    def __eq__(self, other):
        if isinstance(other, IronpipeRun):
            return self.run['id'] == other.run['id']
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.run['id'])

    def __getitem__(self, key):
        return self.run[key]

    def __contains__(self, key):
        return self.run.__contains__(key)

    def __keytransform__(self, key):
        return key

