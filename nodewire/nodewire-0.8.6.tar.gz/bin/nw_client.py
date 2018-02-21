#!/usr/bin/env python3
import asyncio
import websockets
import sys

messages = asyncio.Queue()
cmds = asyncio.Queue()
cp = ''

async def send_loop(websocket):
    while True:
        if not cmds.empty():
            cmd = cmds.get_nowait()
            await websocket.send(cmd)
        if not messages.empty():
            reply = messages.get_nowait()
            print(reply.strip())
        await asyncio.sleep(0)

def got_stdin_data():
    msg = sys.stdin.readline()
    cmds.put_nowait(msg)

async def receive_loop():
    if len(sys.argv)>=2:
        server = sys.argv[1]
    else:
        server = input('connect to:')
    async with websockets.connect('ws://' + server + ':5005') as websocket:
        task = asyncio.Task(send_loop(websocket))

        while True:
            reply = await websocket.recv()
            messages.put_nowait(reply)
try:
    asyncio.get_event_loop().add_reader( sys.stdin, got_stdin_data)
    asyncio.get_event_loop().run_until_complete(receive_loop())
except KeyboardInterrupt:
    pass