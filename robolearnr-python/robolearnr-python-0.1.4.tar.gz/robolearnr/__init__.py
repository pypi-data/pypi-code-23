#!/usr/bin/env python

'''
.. module:: robolearnr
    :platform: Unix, Windows
    :synopsis: Python API to interact with Robolearn
    :noindex:
'''
import urllib2
import json

class Robolearn:

    def __init__(self, url='http://127.0.0.1:9000'):
        self.server = url
        self.__server_rpc('info')

    def forward(self):
        self.__server_rpc('forward')

    def rotate(self):
        self.__server_rpc('rotate')

    def reset(self):
        self.__server_rpc('reset')
        self.__server_rpc('info')

    def before_obstacle(self):
        return self.info['before_obstacle']

    def on_goal(self):
        return self.info['on_goal']

    def __server_rpc(self, action):
        response = urllib2.urlopen('%s/api/%s' % (self.server, action))
        self.info = json.loads(response.read())
