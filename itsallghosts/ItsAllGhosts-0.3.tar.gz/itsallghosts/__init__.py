""" It's All Ghosts - GhostText server for any editor"""

# Copyright (c) 2017 Dominik George <nik@naturalnet.de>
# Copyright (c) 2018 Timothy Sell <timothy.sell@unisys.com>
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


import asyncio
from contextlib import closing
import json
import logging
import os
import socket
import sys
from tempfile import mkstemp, gettempdir

import aiohttp
from aiohttp import web
from aiohttp.web_exceptions import HTTPException
from xdg import XDG_CONFIG_HOME, XDG_RUNTIME_DIR

if XDG_RUNTIME_DIR:
    XDG_RUNTIME_DIR = XDG_RUNTIME_DIR.replace("$HOME",os.path.expanduser("~"))
else:
    # Find temporary directory
    # e.g. Unix=/tmp, Windows=c:\users\<username>\AppData\Local\Temp
    XDG_RUNTIME_DIR = gettempdir()

if XDG_CONFIG_HOME:
    XDG_CONFIG_HOME = XDG_CONFIG_HOME.replace("$HOME",os.path.expanduser("~"))
else:
    XDG_CONFIG_HOME = os.path.join(os.path.expanduser("~"),".config")

# Address to bind on
LISTEN_ADDRESS = '127.0.0.1'

# Editor to spawn
if sys.platform == 'win32':
    USERSCRIPT = os.path.join(XDG_CONFIG_HOME, 'itsallghosts.cmd')
    EDITOR = ['C:\\Program Files\\Notepad++\\notepad++.exe', '-nosession']
else:
    USERSCRIPT = os.path.join(XDG_CONFIG_HOME, 'itsallghosts_cmd')
    EDITOR = ['uxterm', '-e', 'nano']

# If user's own script exists, call that.
#
# On Unix, that script will by default be ~/.config/itsallghosts_cmd,
# and look something like this (for xfte as editor):
#
#     xfte -geometry 80x25 -C/usr/local/lib/fte/normal.fte -d -Ttags "$*"
#
# In Windows, that script will by default be in
# c:\users\<username>\.config\itsallghosts.cmd, and look something like this:
#
#     c:\tools\xfte.exe %*
if os.path.exists(USERSCRIPT):
    if sys.platform == 'win32':
        EDITOR = ['cmd', '/c', USERSCRIPT]
    else:
        EDITOR = ['sh', USERSCRIPT]
logging.info('Using editor: %s' % ' '.join(EDITOR))
logging.debug("%s: XDG_CONFIG_HOME=%s, XDG_RUNTIME_DIR=%s" % (sys.platform,
    XDG_CONFIG_HOME, XDG_RUNTIME_DIR))

# Switch default event loop for Windows
# cf. https://docs.python.org/3/library/asyncio-subprocess.html
if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()

    def _check_ctrl_c():
        """Hack that allows Ctrl+C to cancel the program in Windows.

        Without this, Ctrl+C in Windows is ignored when the program is running.
        Thanks to https://stackoverflow.com/questions/24774980
        and https://groups.google.com/forum/#!topic/python-tulip/pr9fgX8Vh-A.
        The root cause of the problem is that AbstractEventLoop.add_signal_handler() and
        AbstractEventLoop.remove_signal_handler() are not supported in Windows --
        https://docs.python.org/dev/library/asyncio-eventloops.html#platform-support.
        This prevents aiohttp.web.run_app from being able to report the Ctrl+C.
        The workaround here is just to "come up for air" once-per-second to enable SIGINT.
        """
        loop.call_later(1.0, _check_ctrl_c)
    _check_ctrl_c()

    asyncio.set_event_loop(loop)

def is_root():
    """ Return True iff we are the root user on a *nix platform"""

    if sys.platform == 'win32':
        # os.getuid() is not implemented on Windows
        return False
    return (os.getuid() == 0)

def free_port():
    """ Get a random free port """

    # pragma pylint: disable=no-member
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]
    # pragma pylint: enable=no-member

def owner_of_port(port):
    """ Get the owning user id of a TCP connection """
    import psutil

    # Get connection matching port
    conns = psutil.net_connections()
    matches = [conn for conn in conns if conn.laddr.ip == '127.0.0.1' and conn.laddr.port == port]

    if matches:
        # Find user id holding socket with port
        conn = matches[0]
        pid = conn.pid
        process = psutil.Process(pid)
        uid = process.uids().effective
        return uid

def user_runtime_dir(uid):
    """ Guess the XDG_RUNTIME_DIR of a user """

    # Try user runtime directory according to Freedesktop
    rundir = os.path.join(os.path.sep, 'run', 'user', str(uid))
    if os.path.isdir(rundir):
        return rundir

    # Default to /run
    return os.path.join(os.sep, 'run')

async def handle_get(request):
    """ Handler for all HTTP requests """

    # Determine whether this is WebSockets or not
    try:
        wsock = web.WebSocketResponse()
        await wsock.prepare(request)
    except HTTPException:
        # This is not a WebSocket connection

        if is_root():
            # Determine user's port (if running as root, so multi-user mode)
            client_port = request.transport.get_extra_info('peername')[1]
            uid = owner_of_port(client_port)
            port_filen = os.path.join(user_runtime_dir(uid), 'itsallghosts-port')
            with open(port_filen, 'r') as port_fileh:
                port = int(port_fileh.read())
            logging.info('Handing off connection to uid %d' % client_uid)
        else:
            port = 4001
            logging.info('Handling own client connection')
        # Assemble initial JSON response
        res = {'ProtocolVersion': 1, 'WebSocketPort': port}
        return web.json_response(res)

    fileh, filen, process = None, None, None

    # Continue WebSockets conversation
    async for msg in wsock:
        if msg.type == aiohttp.WSMsgType.TEXT:
            # Handle editor information
            data = json.loads(msg.data)
            text = data['text']

            # Check if file is already known
            if not fileh:
                # Create new tempfile and start subprocess
                fileh, filen = mkstemp(suffix='itsallghosts')
                logging.debug('Opened new file %s' % filen)

            # Write text to file
            with open(filen, 'w', encoding='utf-8') as fileh2:
                fileh2.write(text)
                logging.debug('Updated file %s' % filen)

            # Check if process is already running
            if not process:
                # Start subprocess and wait for termination
                process = await asyncio.create_subprocess_exec(*EDITOR, filen)
                logging.debug('Spawned editor for file %s' % filen)

                # Wait for termination
                await process.wait()
                logging.info('Editor exited')
                process = None

                # Get contents of file and send text change event
                with open(filen, 'r', encoding='utf-8') as fileh2:
                    text = fileh2.read()
                res = {'text': text}
                await wsock.send_str(json.dumps(res))

                # Close WebSocket connection
                logging.debug('Closing WebSocket')
                await wsock.close()

    # Clean up
    if fileh:
        os.close(fileh)
        os.unlink(filen)
    if process:
        process.terminate()


    logging.info('Session ended')
    return wsock

def main():
    """ Main function to start up the server """

    # Set up the main HTTP server
    http_app = web.Application()
    http_app.router.add_get('/', handle_get)
    port = 4001

    # Randomise port if run as separate user process
    if len(sys.argv) > 1 and sys.argv[1] == '--user':
        logging.info('Running in multi-user user mode')
        port = free_port()
        logging.info('Got free port %d' % port)

    # Store port in user's run directory
    if not is_root():
        port_filen = os.path.join(XDG_RUNTIME_DIR, 'itsallghosts-port')
        with open(port_filen, 'w')as port_fileh:
            port_fileh.write(str(port))
            logging.debug('Wrote port to %s' % port_filen)

    # Run web server
    web.run_app(http_app, host=LISTEN_ADDRESS, port=port)

if __name__ == '__main__':
    main()
