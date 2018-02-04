import asyncio
import glob
import gzip
import hashlib
import importlib.util
import logging
import os
import re
import signal
import socket
import sys
import threading
from email.utils import formatdate
from logging.handlers import RotatingFileHandler
from traceback import format_exc, print_exc
from urllib.parse import urlparse, parse_qs

import requests
import yaml


class MiniFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt='[%(asctime)s] %(levelname)s: %(message)s%(peer)s', datefmt='%m-%d-%Y %I:%M:%S %p')

    def format(self, record):
        if not hasattr(record, 'peer'):
            record.peer = ''
        else:
            record.peer = ' [' + record.peer + ']'
        return super().format(record)


class MiniFilter(logging.Handler):
    def __init__(self, min, max=None):
        super().__init__()
        self.min = min or logging.NOTSET
        self.max = max or logging.FATAL

    def filter(self, record):
        return self.min <= record.levelno <= self.max

    def emit(self, record):
        super().emit(record)


__version__ = '0.2.0a1'
log = logging.getLogger('minipyp')
log.setLevel(logging.INFO)
stream = logging.StreamHandler()
stream.setFormatter(MiniFormatter())
log.addHandler(stream)


def _default(obj: dict, key, default):
    if key not in obj:
        obj[key] = default


def _except(error: str, extra: dict=None, fatal: bool=False):
    log.fatal(error, extra=extra) if fatal else log.error(error, extra=extra)
    raise Exception(error)


def _translate(config: dict):
    new = {}
    for key, value in config.items():
        key = key.lower().replace(' ', '_').replace('\'', '')
        if type(value) == dict:
            new[key] = _translate(value)
        elif type(value) == list:
            items = value[:]
            new[key] = []
            for item in items:
                if type(item) == dict:
                    item = _translate(item)
                new[key].append(item)
        else:
            new[key] = value
    return new


def _capitalize(string: str, reset: bool=False):
    if reset:
        string = string.lower()
    new = ''
    for i in range(len(string)):
        if i == 0:
            new += string[i].upper()
        elif string[i - 1] == '-':
            new += string[i].upper()
    return string


class Handler:
    def handle(self, minipyp, request):
        _except('Handler for file ' + request.file + ' has no handle() method')


class PyHandler(Handler):
    def handle(self, minipyp, request):
        cwd = os.getcwd()
        cwd_temp = os.path.dirname(request.file)
        os.chdir(cwd_temp)
        if cwd_temp not in sys.path:
            sys.path.append(cwd_temp)
        spec = importlib.util.spec_from_file_location('page', request.file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.render(minipyp, request)
        os.chdir(cwd)
        sys.path.remove(cwd_temp)
        if result is None:
            return b''
        elif type(result) != bytes:
            charset = 'latin_1'
            if 'Content-Type' in request._response_headers:
                if 'charset=' in request._response_headers['Content-Type']:
                    charset = request._response_headers['Content-Type'].split('charset=')[1]
            try:
                return str(result).encode(charset.replace('-', '_'))  # will this cover all encodings?
            except UnicodeEncodeError:
                _except('Non-' + charset + ' value returned by handler, Content-Type does not contain correct encoding')
        return result


class Request:
    """Information about the client's request."""

    def __init__(self, minipyp, server, bare=None, full=None):
        self._status = None
        self._response_headers = {}
        self.bare = bool(bare)
        if full:
            # Full Request object
            proto = full[0].split()
            if len(proto) != 3:
                _except('Failed to parse initial request line', server.extra)
            self.method = proto[0]  #: HTTP method (e.g. POST)
            self.protocol = proto[2]  #: HTTP protocol version (e.g. HTTP/1.1)
            if self.protocol not in ['HTTP/1.0', 'HTTP/1.1']:
                _except('Invalid protocol `' + self.protocol + '`', server.extra)
            self.headers = {}  #: Request headers
            try:
                for line in full[1:]:
                    if line == '':
                        break
                    key, value = line.split(': ', 1)
                    self.headers[_capitalize(key)] = value
            except:
                _except('Headers seem to be malformed', server.extra)
            uri = urlparse(proto[1])
            self.scheme = uri.scheme or 'http'  #: Transfer scheme (e.g. https)
            try:
                self.host = uri.netloc or self.headers['Host']  #: Hostname requested (e.g. localhost)
            except:
                _except('No host was provided in headers or request line', server.extra)
            self.path = uri.path  #: Path requested (e.g. /path/to/file.txt)
            self.uri = uri.path + (('?' + uri.query) if len(uri.query) else '')  #: Path requested, including query
            self.query_string = uri.query  #: Querystring (e.g. A=1&B=2)
            self.query = parse_qs(uri.query, True)  #: Parsed querystring (i.e. GET params)
            if '' in full:
                self.body = '\n'.join(full[full.index('') + 1:])  #: Request body
            self.post = parse_qs(self.body, True)  #: Parsed request body (i.e. POST params)
            self.site = minipyp.get_site(self.host)  #: Effective site config
            self.root = self.site['root'] if self.site else minipyp._config['root']  #: Document root
            self.file = os.path.join(self.root, *self.path.split('/'))  #: File requested
        elif bare:
            # Barebones Request object (for error handling)
            self.protocol = 'HTTP/1.0'
            self.host = None
            self.file = None
            if len(bare):
                args = bare[0].split()
                if len(args) == 3:
                    try:
                        uri = urlparse(args[1])
                        if uri.netloc:
                            self.host = uri.netloc
                            self.path = uri.path
                        else:
                            self.path = uri.path
                    except ValueError:
                        pass
                    if args[2] in ['HTTP/1.0', 'HTTP/1.1', 'HTTP/2.0']:
                        self.protocol = args[2]
            self.headers = {}
            for line in bare[1:]:
                if line == '':
                    break
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    self.headers[_capitalize(key)] = value
            if not self.host and 'Host' in self.headers:
                self.host = self.headers['Host']
            if self.host:
                self.site = minipyp.get_site(self.host)
                self.root = self.site['root'] if self.site else minipyp._config['root']
                if self.path:
                    self.file = os.path.join(self.root, *self.path.split('/'))

    def set_header(self, name: str, value: str):
        """
        Set a header in the response, capitalized Like-This.

        :param name: header name, e.g. "X-My-Header"
        :param value: header value, e.g. "My Value"
        """
        self._response_headers[_capitalize(name)] = value

    def set_status(self, status: str):
        """
        Set the response status.

        :param status: full status string (e.g. "404 Not Found"
        """
        self._status = status


class Server(asyncio.Protocol):
    def __init__(self, minipyp):
        self._minipyp = minipyp
        self._loop = asyncio.get_event_loop()
        self._transport = None
        self._keepalive = None
        self._timeout = minipyp._config['timeout']
        self._timing = None
        self.peer = None
        self.extra = {
            'peer': 'unknown peer'
        }

    def connection_made(self, transport):
        self.peer = transport.get_extra_info('peername')
        self.extra['peer'] = ':'.join(self.peer)
        self._transport = transport
        self._keepalive = True
        if self._timeout:
            self._timing = self._loop.call_later(self._timeout, self.on_timeout)
        log.debug('Connected', extra=self.extra)

    def connection_lost(self, e):
        if e:
            log.warning('Connection lost: ' + str(e), extra=self.extra)

    def data_received(self, data):
        lines = list(map(lambda x: x.decode('utf-8'), data.split(b'\r\n')))
        if len(lines):
            try:
                request = Request(self._minipyp, self, full=lines)
                log.info(request.method + ' ' + request.path, extra=self.extra)
                request.site = self._minipyp.get_site(request.host)
                path_opts = self._minipyp.get_path(request.path, request.site)
                proxy = None
                if path_opts['proxy']:
                    proxy_p = urlparse(path_opts['proxy'])
                    proxy = proxy_p.scheme + '://' + proxy_p.netloc
                    request.uri = proxy_p.path + request.uri
                if proxy:
                    log.info('Forwarding client to: ' + proxy + request.uri, extra=self.extra)
                    if 'X-Forwarded-Host' not in request.headers:
                        request.headers['X-Forwarded-Host'] = request.host
                    try:
                        r = requests.request(request.method, proxy + request.uri, stream=True,
                                             headers=request.headers, data=request.body)
                        request.set_status(str(r.status_code) + ' ' + r.reason)
                        request._response_headers = r.headers
                        if r.headers.get('Transfer-Encoding', '') == 'chunked':
                            i = 0
                            for chunk in r.iter_content(chunk_size=None):
                                chunk = hex(len(chunk))[2:].encode('latin_1') + b'\r\n' + chunk + b'\r\n'
                                if i == 0:
                                    self._respond(request, chunk)
                                else:
                                    self._write(chunk)
                                i += 1
                            self._write(b'0\r\n\r\n')
                        else:
                            self._respond(request, r.content)
                        r.close()
                    except:
                        print_exc()
                        self._give_error(request, 502, traceback=format_exc())
                else:
                    request.root = request.site['root'] if request.site else self._minipyp._config['root']
                    if request.protocol == 'HTTP/1.1':
                        self._keepalive = request.headers['Connection'] != 'close'
                    else:
                        self._keepalive = request.headers['Connection'] == 'Keep-Alive'
                    match = re.match(r'timeout=(\d+)', request.headers.get('Keep-Alive', ''))
                    if match:
                        timeout = int(match.group(1))
                        if timeout < self._timeout:
                            self._timeout = timeout
                    path = list(filter(None, request.path.split('?')[0].split('/')))
                    path = [''] + path
                    file = None
                    full_ospath = os.path.join(request.root, *path)
                    options = self._minipyp.get_directory(full_ospath)
                    if options['public']:
                        for i in range(len(path)):
                            ospath = full_ospath if i == 0 else os.path.join(request.root, *path)
                            viewing_dir = i == 0 and os.path.isdir(ospath)
                            if viewing_dir:
                                matches = glob.glob(os.path.join(ospath, 'index.*'))
                                if len(matches):
                                    file = matches[0]
                                    break
                            if os.path.isfile(ospath):
                                file = ospath
                                break
                            if not os.path.isdir(ospath):
                                matches = glob.glob(ospath + '.*')
                                if len(matches) and os.path.isfile(matches[0]):
                                    file = matches[0]
                                    break
                            if os.path.isfile(os.path.join(ospath, '.static')):
                                break
                            if not options['static']:
                                matches = glob.glob(os.path.join(ospath, 'catchall.*'))
                                if len(matches):
                                    file = matches[0]
                                    break
                            if viewing_dir:
                                if options['indexing']:
                                    request.set_header('Content-Type', 'text/html')
                                    (_, dirs, fils) = next(os.walk(ospath))
                                    index = '<strong>Files</strong>\n        <ul>\n'
                                    for fil in fils:
                                        index += '            <li><a href="' + fil + '">' + fil + '</a></li>\n'
                                    if not len(fils):
                                        index += '            <small>(none)</small>\n'
                                    index += '        </ul>\n        <strong>Directories</strong>\n        <ul>\n'
                                    for dir in dirs:
                                        index += '            <li><a href="' + dir + '/">' + dir + '/</a></li>\n'
                                    if not len(dirs):
                                        index += '            <small>(none)</small>\n'
                                    index += '        </ul>'
                                    response = self._minipyp._index.format(request.path, index, __version__)
                                    self._respond(request, response.encode('utf-8'))
                                    file = False
                                    break
                                self._give_error(request, 403)
                            path.pop()
                        if file is None:
                            self._give_error(request, 404)
                        elif file is not False:
                            log.debug('Serving file: ' + file, extra=self.extra)
                            request.file = file
                            self._respond(request, self._render(request, file, options))
                    else:
                        self._give_error(request, 403)
            except:
                print_exc()
                self._give_error(Request(self._minipyp, self, bare=lines), 500, traceback=format_exc())
        else:
            self._keepalive = False
        if not self._keepalive:
            if self._timing:
                self._timing.cancel()
            self._transport.close()
        if self._timeout and self._timing:
            self._timing.cancel()
            self._timing = self._loop.call_later(self._timeout, self.on_timeout)

    def on_timeout(self):
        log.debug('Connection timed out', extra=self.extra)
        self._transport.close()

    def _give_error(self, request: Request, error: int, **kwargs):
        status = {
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error',
            502: 'Bad Gateway'
        }[error]
        request.set_status(str(error) + ' ' + status)
        page = self._minipyp.get_error_page(error, request.file)
        html = 'MiniPyP encountered a ' + str(error) + '. The custom error page is missing or invalid.'
        if 'file' in page:
            if os.path.isfile(page['file']):
                html = self._render(request, page['file'])
        elif 'html' in page:
            html = page['html']
            if not request.bare:
                kwargs['uri'] = request.path
            for var, value in kwargs.items():
                html = html.replace('{' + var + '}', value)
            request.set_header('Content-Type', 'text/html')
        if type(html) == str:
            html = html.encode('utf-8')
        self._respond(request, html)

    def _render(self, request: Request, file: str, opts=None):
        ext = file.split('.')[-1]
        handle = not opts or ext not in opts['dont_handle']
        mime = self._minipyp.get_mime_type(ext) or 'text/plain'
        request.set_header('Content-Type', mime if handle else 'text/plain')
        if handle:
            handler = self._minipyp.get_handler(ext)
            if handler:
                return handler.handle(self._minipyp, request)
        request.set_header('Last-Modified', formatdate(timeval=os.path.getmtime(file), usegmt=True))
        with open(file, 'rb') as f:
            return f.read()

    def _respond(self, request: Request, data: bytes):
        self._write((request.protocol + ' ' + (request._status or '200 OK')).encode('utf-8'))
        if self._keepalive:
            request.set_header('Keep-Alive', 'timeout=' + str(self._timeout))
        if 'Content-Type' not in request._response_headers:
            request.set_header('Content-Type', 'text/plain')
        request.set_header('Date', formatdate(usegmt=True))
        request.set_header('Server', 'MiniPyP/' + __version__)
        has_body = False
        if data is not None and len(data) and (request.bare or request.method != 'HEAD'):
            has_body = True
            if request._response_headers.get('Transfer-Encoding', '') != 'chunked':
                data = gzip.compress(data)
                sha1 = hashlib.sha1()
                sha1.update(data)
                request.set_header('Etag', '"' + sha1.hexdigest() + '"')
                request.set_header('Content-Length', str(len(data)))
                if 'gzip' in request.headers.get('Accept-Encoding', ''):
                    request.set_header('Content-Encoding', 'gzip')
                    request.set_header('Vary', 'Accept-Encoding')
        for key, value in request._response_headers.items():
            self._write((key + ': ' + value).encode('utf-8'))
        self._write(b'')
        if has_body:
            self._write(data)

    def _write(self, data: bytes):
        self._transport.write(data + (b'\r\n' if data[-2:] != b'\r\n' else b''))


class ConfigError(ValueError):
    def __init__(self, *args):
        super().__init__(*args)


class MiniPyP:
    _error_template = '''<html>
<head>
        <title>{0}</title>
        <style>
            html {{
                background: #f8f8f8;
                font-family: Helvetica, Arial, sans-serif;
            }}
            body {{
                padding: 20px;
            }}
            hr {{
                border: none;
                border-top: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <h1>{0}</h1>
        {1}
        <hr>
        <small>Powered by MiniPyP {2}</small>
    </body>
</html>'''
    _index = '''<html>
<head>
        <title>Index of {0}</title>
        <style>
            html {{
                background: #f8f8f8;
                font-family: Helvetica, Arial, sans-serif;
            }}
            body {{
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Index of {0}</h1>
        {1}
        <hr>
        <small>Powered by MiniPyP {2}</small>
    </body>
</html>'''

    def __init__(self, config):
        """
        Configure the MiniPyP server.

        :param config: YAML config file or dict of values
        """
        self._config = None
        self._config_file = None
        self._loop = None
        self._coro = None
        self._handlers = {}

        self.load_config(config)

        # Setup log files
        log_level = logging.INFO
        if 'log_level' in self._config:
            log_level = logging._nameToLevel[self._config['log_level'].upper()]
        log_limit = 25
        if 'log_limit' in self._config:
            log_limit = int(self._config['log_limit'])
        if 'log' in self._config:
            handler = RotatingFileHandler(self._config['log'], maxBytes=log_limit * 1024)
            handler.setFormatter(MiniFormatter())
            handler.addFilter(MiniFilter(log_level, max=logging.WARNING))
            log.addHandler(handler)
        if 'error_log' in self._config:
            handler = RotatingFileHandler(self._config['error_log'], maxBytes=log_limit * 1024)
            handler.setFormatter(MiniFormatter())
            handler.addFilter(MiniFilter(logging.WARNING))
            log.addHandler(handler)

        # Set defaults
        if 'host' not in self._config:
            self._config['host'] = '0.0.0.0'
        if 'port' not in self._config:
            self._config['port'] = 80
        if 'timeout' not in self._config:
            self._config['timeout'] = 15
        if 'error_pages' not in self._config:
            self._config['error_pages'] = {}
        if 'mime_types' not in self._config:
            self._config['mime_types'] = {}
        if 'sites' not in self._config:
            self._config['sites'] = []
        if 'directories' not in self._config:
            self._config['directories'] = {}
        if 'paths' not in self._config:
            self._config['paths'] = {}
        if 403 not in self._config['error_pages']:
            self.set_error_page(403, {
                'html': self._error_template.format('403 Forbidden',
                                                    '<p>You don\'t have permission to view this page.</p>',
                                                    __version__)
            })
        if 404 not in self._config['error_pages']:
            self.set_error_page(404, {
                'html': self._error_template.format('404 Not Found',
                                                    '''<p>The requested page could not be found:</p>
        <p><code>{uri}</code></p>''',
                                                    __version__)
            })
        if 500 not in self._config['error_pages']:
            self.set_error_page(500, {
                'html': self._error_template.format('500 Internal Server Error',
                                                    '''<p>An error occurred while displaying this page:</p>
        <pre>{traceback}</pre>''',
                                                    __version__)
            })
        if 502 not in self._config['error_pages']:
            self.set_error_page(502, {
                'html': self._error_template.format('502 Bad Gateway',
                                                    '''<p>An error occurred with the server handling this request:</p>
        <pre>{traceback}</pre>''',
                                                    __version__)
            })
        self.set_mime_type('text/html', 'html', 'shtml', 'htm')
        self.set_mime_type('text/css', 'css')
        self.set_mime_type('text/csv', 'csv')
        self.set_mime_type('application/xml', 'xml', 'rdf')
        self.set_mime_type('application/javascript', 'js')
        self.set_mime_type('application/xml', 'xml', 'rdf')
        self.set_mime_type('application/rss+xml', 'rss')
        self.set_mime_type('application/octet-stream', 'bin', 'dll', 'dmg', 'exe', 'img', 'iso', 'msi', 'safariextz')
        self.set_mime_type('application/pdf', 'pdf')
        self.set_mime_type('application/rtf', 'rtf')
        self.set_mime_type('application/x-7z-compressed', '7z')
        self.set_mime_type('application/x-bittorrent', 'torrent')
        self.set_mime_type('application/x-chrome-extension', 'crx')
        self.set_mime_type('application/x-opera-extension', 'oex')
        self.set_mime_type('application/x-rar-compressed', 'rar')
        self.set_mime_type('application/x-redhat-package-manager', 'rpm')
        self.set_mime_type('application/x-x509-ca-cert', 'crt', 'der', 'pem')
        self.set_mime_type('application/x-shockwave-flash', 'swf')
        self.set_mime_type('application/xhtml+xml', 'xhtml')
        self.set_mime_type('application/zip', 'zip')
        self.set_mime_type('application/perl', 'pl')
        self.set_mime_type('application/font-woff', 'woff')
        self.set_mime_type('application/font-woff2', 'woff2')
        self.set_mime_type('application/vns.ms-fontobject', 'eot')
        self.set_mime_type('application/x-font-ttf', 'ttf', 'ttc')
        self.set_mime_type('audio/midi', 'mid', 'midi')
        self.set_mime_type('audio/mp4', 'aac', 'm4a')
        self.set_mime_type('audio/mpeg', 'mp3')
        self.set_mime_type('audio/ogg', 'ogg')
        self.set_mime_type('audio/x-wav', 'wav')
        self.set_mime_type('image/bmp', 'bmp')
        self.set_mime_type('image/gif', 'gif')
        self.set_mime_type('image/jpeg', 'jpg', 'jpeg')
        self.set_mime_type('image/png', 'png', 'apng')
        self.set_mime_type('image/svg+xml', 'svg')
        self.set_mime_type('image/x-icon', 'ico', 'cur')
        self.set_mime_type('image/tiff', 'tif', 'tiff')
        self.set_mime_type('video/mp4', 'mp4', 'm4v')
        self.set_mime_type('video/ogg', 'ogv')
        self.set_mime_type('video/quicktime', 'mov')
        self.set_mime_type('video/webm', 'webm')
        self.set_mime_type('video/x-flv', 'flv')
        self.set_mime_type('video/x-ms-wmv', 'wmv')
        self.set_mime_type('video/x-msvideo', 'avi')
        self.set_mime_type('font/opentype', 'otf')
        self.set_handler('py', 'text/html', PyHandler())
        self.loop = None
        self.coro = None

    def start(self):
        """Start the server."""
        log.debug('Starting server')
        if sys.platform == 'win32':
            asyncio.set_event_loop(asyncio.ProactorEventLoop())
        self.loop = asyncio.get_event_loop()
        if sys.platform == 'win32':
            # Get a little hacky for Windows
            if threading.current_thread() == threading.main_thread():
                for term in ('SIGINT', 'SIGTERM'):
                    signal.signal(getattr(signal, term), self.stop)
            self.loop.call_later(0.1, self._wakeup)
        else:
            for term in ('SIGINT', 'SIGTERM'):
                self.loop.add_signal_handler(getattr(signal, term), self.stop)
            if hasattr(signal, 'SIGHUP'):
                self.loop.add_signal_handler(signal.SIGHUP, self.load_config)
        self.coro = self.loop.create_server(lambda: Server(self), self._config['host'], self._config['port'])
        self.loop.run_until_complete(self.coro)
        log.info('Listening on ' + self._config['host'] + ':' + str(self._config['port']) + '...')
        try:
            self.loop.run_forever()
        except asyncio.CancelledError:
            log.warning('Server shut down before all tasks could complete')
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop the server."""
        log.info('Shutting down...')
        if self.coro:
            self.coro.close()
        if self.loop:
            self.loop.stop()
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def load_config(self, config=None):
        """
        Load new config values from the provided dict.
        If None, and a previously loaded file exists, it will be reloaded.

        :param config: the new config
        """
        if not config:
            config = self._config_file
        if type(config) == str:
            try:
                with open(config) as conf:
                    self._config_file = config
                    config = _translate(yaml.load(conf))
            except (IOError, yaml.YAMLError) as e:
                _except('Failed to read config file: ' + str(e), fatal=True)
        elif type(config) == dict:
            self._config_file = None
        else:
            _except('Invalid config provided (must be a file path or a dict)', fatal=True)
        try:
            self.test_config(config)
            self._config = config
        except ConfigError as e:
            _except('Malformed config: ' + str(e), fatal=True)
        log.info('Configuration reloaded from disk')

    def _wakeup(self):
        self.loop.call_later(0.1, self._wakeup)

    def add_site(self, site: dict):
        """
        Add a site after initialization.

        :param site: the same dict as in the configuration
        """
        config = self._config
        config['sites'].append(site)
        self.test_config(config, 'sites')
        self._config = config

    def get_site(self, host: str):
        """
        Get a site by its hostname.

        :param host: the hostname to look for
        :return: dict or None
        """
        for site in self._config['sites']:
            if host.lower() in site['uris']:
                return site
        return None

    def set_handler(self, extension: str, mime_type: str, handler: Handler):
        """
        Add a file handler after initialization.

        :param extension: the file extension (e.g. 'py')
        :param mime_type: the MIME type to serve with this file
        :param handler: a Handler subclass (see Handler docs)
        """
        config = self._config
        extension = extension.lower()
        if extension in self._handlers:
            raise ConfigError('a handler already exists for filetype: ' + extension)
        self.set_mime_type(mime_type, extension)
        self._handlers[extension] = handler
        self.test_config(config, 'handlers')
        self._config = config

    def get_handler(self, extension: str):
        """
        Get a file handler by the extension.

        :param extension: the file extension (e.g. 'py')
        :return: Handler object or None
        """
        if extension in self._handlers:
            return self._handlers[extension]
        return None

    def set_mime_type(self, mime_type, *extensions):
        """
        Set the MIME type of a file extension.

        :param mime_type: MIME type (e.g. 'application/html'
        :param extensions: File extensions (e.g. 'py', 'pyc', ...)
        """
        extensions = list(extensions)
        config = self._config
        for type, exts in config['mime_types'].items():
            for ext in extensions:
                if ext.lower() in exts:
                    config['mime_types'][mime_type].remove(ext)
        if mime_type in config['mime_types']:
            config['mime_types'][mime_type] += extensions
        else:
            config['mime_types'][mime_type] = extensions
        self.test_config(config, 'mime_types')
        self._config = config

    def get_mime_type(self, extension):
        """
        Get the MIME type for any file extension.

        :param extension: the file extension
        :return: MIME type or None if one is not set
        """
        for type, exts in self._config['mime_types'].items():
            if extension.lower() in exts:
                return type
        return None

    def set_path(self, path: str, options: dict=None):
        """
        Set the options for a path. If options is None, all options will be removed.
        Otherwise, any options not provided will stay as-is in the configuration.

        :param path: URI path
        :param options: the options to set
        """
        config = self._config
        updated = False
        for spath, opts in config['paths'].items():
            if spath == path:
                if not options:
                    del config['paths'][path]
                else:
                    for name, value in options.items():
                        config['paths'][path][name] = value
                updated = True
        if not updated:
            config['paths'][path] = options
        self.test_config(config, 'paths')
        self._config = config

    def get_path(self, path: str, site: dict=None):
        """
        Get the options for any given path, defaulting if no options were set.
        If a site is given, it will be applied after any global options for the path.

        :param path: URI (e.g. '/mypath')
        :param site: site object (see MiniPyP.get_site)
        :return: dict
        """
        options = {
            'proxy': None
        }
        for cpath in sorted(self._config['paths'], key=len):
            cpath = str(cpath)
            opts = self._config['paths'][cpath]
            if path.startswith(cpath) or re.match(cpath, path):
                if 'proxy' in opts:
                    options['proxy'] = opts['proxy']
        if site and 'paths' in site:
            for cpath in sorted(site['paths'], key=len):
                cpath = str(cpath)
                opts = site['paths'][cpath]
                if path.startswith(cpath) or re.match(cpath, path):
                    if 'proxy' in opts:
                        options['proxy'] = opts['proxy']
        return options

    def set_directory(self, dir: str, options: dict=None):
        """
        Set the options for a directory. If options is None, all options will be removed.
        Otherwise, any options not provided will stay as-is in the configuration.

        :param dir: OS-specific directory path
        :param options: the options to set
        """
        config = self._config
        for sdir, opts in config['paths'].items():
            if sdir == dir:
                if not options:
                    del config['directories'][dir]
                else:
                    for name, value in options.items():
                        config['directories'][dir][name] = value
                return
        config['directories'][dir] = options
        self.test_config(config, 'directories')
        self._config = config

    def get_directory(self, dir: str):
        """
        Get the options for any given directory, defaulting if no options were set.

        :param dir: OS-specific directory path
        :return: dict
        """
        options = {
            'public': True,
            'static': False,
            'indexing': True,
            'dont_handle': [],
            'error_pages': self._config['error_pages']
        }
        for path in sorted(self._config['directories'], key=len):
            path = str(path)
            opts = self._config['directories'][path]
            if dir.startswith(path) or re.match(path, dir):
                if 'public' in opts:
                    options['public'] = opts['public']
                if 'static' in opts:
                    options['static'] = opts['static']
                if 'indexing' in opts:
                    options['indexing'] = opts['indexing']
                if 'dont_handle' in opts:
                    options['dont_handle'] = opts['dont_handle']
                if 'error_pages' in opts:
                    for status, page in opts['error_pages'].items():
                        options['error_pages'][status] = page
        return options

    def set_error_page(self, code: int, page: dict):
        """
        Set the error page for any HTTP code.
        Page should include either `html` for plain HTML or `file` to render a file instead.

        :param code: HTTP status
        :param page: dict
        """
        config = self._config
        config['error_pages'][code] = page
        self.test_config(config, 'error_pages')
        self._config = config

    def get_error_page(self, code: int, directory: str=None):
        """
        Get the error page for any HTTP code.

        :param code: HTTP status
        :param directory: OS-specific path to get custom error pages for
        :return: dict
        """
        pages = self.get_directory(directory)['error_pages'] if directory else self._config['error_pages']
        if code in pages:
            return pages[code]
        return None

    def write_config(self, to: str=None):
        """
        Writes the current configuration to the config file.
        If `to` is None (default), the config will be written to the real config file or a ConfigError will be thrown.
        If `to` is False, nothing will be written.

        :param to: the file to write to
        :return: YAML-encoded configuration
        """
        if not self._config_file:
            raise ConfigError('no config file to write to')
        data = yaml.dump(self._config)
        if to is None:
            to = self._config_file
        if to:
            try:
                with open(self._config_file, 'r') as conf:
                    conf.write(data)
            except IOError as e:
                raise ConfigError('failed to write to config file: ' + str(e))
        return data

    def reload_config(self):
        """Reloads the configuration file from disk."""
        if not self._config_file:
            raise ConfigError('no config file to reload')
        try:
            with open(self._config_file) as conf:
                config = yaml.load(conf)
                self.test_config(config)
                self._config = config
        except (IOError, yaml.YAMLError) as e:
            _except('Failed to read config file: ' + str(e), fatal=True)

    @staticmethod
    def test_config(config: dict, part: str=None):
        """
        Test the provided configuration, or a part of it.

        :param config: dict of config
        :param part: part of the config to test (or None)
        :raise: ConfigError if invalid
        """
        if not part:
            if type(config) != dict:
                raise ConfigError('config must be a dict')
            if 'root' not in config:
                raise ConfigError('no `Root` provided')
            if not os.path.isdir(config['root']):
                raise ConfigError('`Root` directory not found')
            if 'host' in config:
                try:
                    socket.gethostbyname(config['host'])
                except socket.gaierror as e:
                    raise ConfigError('`Host` is an invalid hostname: ' + str(e))
            if 'port' in config and (type(config['port']) != int or not 0 < config['port'] < 65536):
                raise ConfigError('`Port` must be a valid port number')
            if 'timeout' in config and type(config['timeout']) != int:
                raise ConfigError('`Timeout` must be an integer of seconds')
            if 'log_level' in config and \
                    config['log_level'].upper() not in logging._nameToLevel.keys():
                raise ConfigError('`Log Level` must be in: ' + ', '.join(logging._nameToLevel.keys()))
            if 'log_limit' in config and type(config['log_limit']) != int:
                raise ConfigError('`Log Limit` must be an integer of megabytes')
            if not os.path.isdir(config['root']):
                raise ConfigError('directory `Root` could not be found')
        if 'sites' in config and (not part or part == 'sites'):
            if type(config['sites']) != list:
                raise ConfigError('`Sites` must be a list')
            for site in config['sites']:
                if type(site['uris']) != list:
                    raise ConfigError('site `URIs` must be a list')
                if 'root' in site and not os.path.isdir(site['root']):
                    raise ConfigError('`Root` directory for site ' + site['URIs'] + ' could not be found')
        if 'mime_types' in config and (not part or part == 'mime_types'):
            if type(config['mime_types']) != dict:
                raise ConfigError('`MIME Types` must be a dict[type, extensions]')
            for mime, exts in config['mime_types'].items():
                if not re.match(r'^[-\w]+/[-\w+.]+$', mime):
                    raise ConfigError('`MIME Types` key must be a valid MIME type')
                if type(exts) != list:
                    raise ConfigError('`MIME Types` value must be a list of extensions')
                for ext in exts:
                    if not re.match(r'^\w+$', ext):
                        raise ConfigError('`MIME Types` extensions should only contain letters (e.g. ["py", "pyc"])')
        if 'error_pages' in config and (not part or part == 'error_pages'):
            if type(config['error_pages']) != dict:
                raise ConfigError('`Error Pages` must be a dict[code, page]')
            for code, page in config['error_pages'].items():
                if type(code) != int or not (300 <= code < 600):
                    raise ConfigError('`Error Pages` key must be a valid HTTP status code')
                if 'html' not in page and 'file' not in page:
                    raise ConfigError('`Error Pages` value must contain a `File` or `HTML`')
                if 'file' in page and not os.path.isfile(page['file']):
                    log.warning('File for error ' + str(code) + ' does not exist')
        if 'directories' in config and (not part or part == 'directories'):
            if type(config['directories']) != dict:
                raise ConfigError('`Directories` must be a dict[path, options]')
            for path, opts in config['directories'].items():
                if not os.path.exists(path):
                    log.warning('Directory in config does not exist: ' + path)
                if 'public' in opts and type(opts['public']) != bool:
                    raise ConfigError('`Public` must be True or False in directory: ' + path)
                if 'static' in opts and type(opts['static']) != bool:
                    raise ConfigError('`Static` must be True or False in directory: ' + path)
                if 'indexing' in opts and type(opts['indexing']) != bool:
                    raise ConfigError('`Indexing` must be True or False in directory: ' + path)
                if 'dont_handle' in opts and type(opts['dont_handle']) != bool:
                    raise ConfigError('`Don\'t Handle` must be True or False in directory: ' + path)
                if 'error_pages' in opts:
                    if type(opts['error_pages']) != dict:
                        raise ConfigError('`Error Pages` must be a dict[code, page] in directory: ' + path)
                    for code, page in opts['error_pages'].items():
                        if type(code) != int or not (300 <= code < 600):
                            raise ConfigError('`Error Pages` key must be a valid HTTP status code in directory' + path)
                        if 'html' not in page and 'file' not in page:
                            raise ConfigError('`Error Pages` value must contain a `File` or `HTML` in directory: ' + path)
                        if 'file' in page and not os.path.isfile(page['file']):
                            log.warning('File for error ' + str(code) + ' does not exist in directory: ' + path)
        if 'paths' in config and (not part or part == 'paths'):
            if type(config['paths']) != dict:
                raise ConfigError('`Paths` must be a dict[path, options]')
            for path, opts in config['paths'].items():
                if 'proxy' in opts:
                    try:
                        uri = urlparse(opts['proxy'])
                        if not all([uri.scheme, uri.netloc]):
                            raise Exception()
                    except Exception as e:
                        raise ConfigError('`Proxy` must be a valid URL in path: ' + path + ' - ' + str(e))