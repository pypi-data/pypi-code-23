"""
Simple HTTP server to check postgres cluster status
"""

import socket

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from BaseHTTPServer import SocketServer
from SocketServer import ThreadingMixIn

from .configuration import Configuration, DEFAULT_CONFIG_PATH
from .database import DatabaseStatus


# Monkey patch finish() method to not crash when client closes connection prematurely
def finish(self, *args, **kwargs):
    try:
        if not self.wfile.closed:
            self.wfile.flush()
            self.wfile.close()
    except socket.error:
        pass
    self.rfile.close()
SocketServer.StreamRequestHandler.finish = finish



class DatabaseStatusHandler(BaseHTTPRequestHandler):
    """
    Check postgres database status
    """

    def handle(self):
        try:
            return BaseHTTPRequestHandler.handle(self)
        except socket.error:
            pass

    def do_GET(self):
        """
        Get server status
        """

        try:

            if self.server.status.is_slave:
                status = 'PostgreSQL slave is running'
            elif not self.server.status.is_readonly:
                status = 'PostgreSQL master is running'
            else:
                status = 'PostgreSQL server is running'

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('{0}\n'.format(status))

        except Exception as e:

            self.send_response(503)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('PostgreSQL server is DOWN\n')


class StatusMonitoringServer(ThreadingMixIn, HTTPServer):
    """
    Status monitoring server for postgres
    """
    def __init__(self, dbname=None, configuration=DEFAULT_CONFIG_PATH):
        self.configuration = Configuration(dbname, configuration)
        self.status = DatabaseStatus(self.configuration)

        print('Starting postgres status monitoring server')
        HTTPServer.__init__(self, ('', self.configuration['httpd']['port']), DatabaseStatusHandler)

    def run(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            print('Shutting down postgres status monitoring server')
            self.socket.close()

