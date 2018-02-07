#!/usr/bin/env python3
from nodewire.NodeWire import NodeWire
import asyncio
import configparser
from nodewire.client import client
import sys
import json
import time

class Node:
    def __init__(self, client):
        self.nw = NodeWire(client, 'nwscript',process=self.process)
        self.terminated = False

    def prompt(self):
        print('---- '),

    def process(self, msg):
        if msg.Command == 'portvalue':
            if msg.Params[0] == 'script':
                s = json.loads(msg.Params[1])
                for line in s:
                    print(line)
                self.prompt()

    def got_stdin_data(self):
        cmd = sys.stdin.readline()
        if cmd.startswith('quit'):
            self.terminated = True
            print('closing...')
            quit()
        else:
            node.nw.send('re', 'set', 'scriptlet', '["' + cmd.strip() + '"]')


if __name__ == '__main__':
    global Prompt
    while True:
        print('NodeWire Interactive shell')
        print('Copyright 2017')
        print('connecting ...')
        config = configparser.RawConfigParser()

        node = Node(client())
        loop = asyncio.get_event_loop()
        loop.add_reader(sys.stdin, node.got_stdin_data)
        node.prompt()

        try:
            node.nw.run()
        except Exception  as ex:
            print(ex)

        time.sleep(10)
