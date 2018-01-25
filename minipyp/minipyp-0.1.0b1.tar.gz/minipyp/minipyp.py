import asyncio
import glob
import gzip
import hashlib
import importlib.util
import os
import re
import signal
import sys
from email.utils import formatdate
from traceback import format_exc
from urllib.parse import urlparse, parse_qs

__version__ = '0.1.0b1'


def _default(obj: dict, key, default):
    if key not in obj:
        obj[key] = default


class Handler:
    def handle(self, minipyp, request):
        raise Exception('Handler requires handle()')


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
        if type(result) == str:
            charset = 'utf-8'
            if 'Content-Type' in request._response_headers:
                if 'charset=' in request._response_headers['Content-Type']:
                    charset = request._response_headers['Content-Type'].split('charset=')[1]
            result = result.encode(charset)
        return result


class Request:
    def __init__(self, server=None, bare=None, full=None):
        self._status = None
        self._response_headers = {}
        self.bare = bool(bare)
        if full:
            # Full Request object
            self.peer = server._peer
            proto = full[0].split()
            if len(proto) != 3:
                raise Exception('Invalid request line')
            self.method = proto[0]
            self.protocol = proto[2]
            if self.protocol not in ['HTTP/1.0', 'HTTP/1.1']:
                raise Exception('Invalid protocol')
            self.headers = {}
            try:
                for line in full[1:]:
                    if line == '':
                        break
                    key, value = line.split(': ', 1)
                    self.headers[key] = value
            except:
                raise Exception('Malformed headers')
            uri = urlparse(proto[1])
            self.scheme = uri.scheme or 'http'  # TODO SSL
            try:
                self.host = uri.netloc or self.headers['Host']
            except:
                raise Exception('No host provided')
            self.path = uri.path
            self.uri = uri.path + (('?' + uri.query) if len(uri.query) else '')
            self.query = parse_qs(uri.query, True)
            if '' in full:
                self.body = '\n'.join(full[full.index('') + 1:])
            self.post = parse_qs(self.body, True)
            self.site = None
            self.root = None
            self.file = None
        elif bare:
            # Barebones Request object (for error handling)
            self.protocol = 'HTTP/1.0'
            if len(bare):
                if bare[:5] == 'HTTP/' and ' ' in bare:
                    self.protocol = bare.split()[0]
            self.headers = {}
            for line in bare[1:]:
                if line == '':
                    break
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    self.headers[key] = value

    def set_header(self, name: str, value: str):
        self._response_headers[name] = value

    def set_status(self, status: str):
        self._status = status


class Server(asyncio.Protocol):
    def __init__(self, minipyp):
        self._minipyp = minipyp
        self._loop = asyncio.get_event_loop()
        self._transport = None
        self._keepalive = None
        self._timeout = minipyp._timeout
        self._timing = None
        self._peer = '[unknown]'

    def connection_made(self, transport):
        self._peer = transport.get_extra_info('peername')
        self._transport = transport
        self._keepalive = True
        if self._timeout:
            self._timing = self._loop.call_later(self._timeout, self.on_timeout)

    def connection_lost(self, e):
        if e:
            print('[' + self._peer[0] + '] Connection lost')
            print(e)

    def data_received(self, data):
        print(data)
        lines = list(map(lambda x: x.decode('utf-8'), data.split(b'\r\n')))
        if len(lines):
            try:
                request = Request(self, full=lines)
                print('[' + self._peer[0] + '] ' + request.method + ' ' + request.path)
                request.site = self._minipyp.get_site(request.host)
                request.root = request.site['root'] if request.site else self._minipyp._root
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
                options = self._minipyp.get_options(full_ospath)
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
                            if len(matches):
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
                                index = '''<strong>Files</strong>
        <ul>
'''
                                for fil in fils:
                                    index += '            <li><a href="' + fil + '">' + fil + '</a></li>\n'
                                if not len(fils):
                                    index += '            <small>(none)</small>\n'
                                index += '''        </ul>
        <strong>Directories</strong>
        <ul>
'''
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
                        request.file = file
                        self._respond(request, self._render(request, file, options))
                else:
                    self._give_error(request, 403)
            except:
                self._give_error(Request(bare=lines), 500, traceback=format_exc())
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
        print('[' + self._peer[0] + '] Timed out')
        self._transport.close()

    def _give_error(self, request: Request, error: int, **kwargs):
        status = {403: 'Forbidden', 404: 'Not Found', 500: 'Internal Server Error'}[error]
        request.set_status(str(error) + ' ' + status)
        page = self._minipyp._error_pages[error]
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
            html = html.encode('utf-8')
            request.set_header('Content-Type', 'text/html')
        self._respond(request, html)

    def _render(self, request: Request, file: str, opts=None):
        ext = file.split('.')[-1]
        handle = not opts or ext not in opts['dont_handle']
        mime = self._minipyp._mime_types[ext.lower()] if ext.lower() in self._minipyp._mime_types else 'text/plain'
        request.set_header('Content-Type', mime if handle else 'text/plain')
        if ext in self._minipyp._handlers and handle:
            return self._minipyp._handlers[ext].handle(self._minipyp, request)
        request.set_header('Last-Modified', formatdate(timeval=os.path.getmtime(file), usegmt=True))
        with open(file, 'rb') as f:
            return f.read()

    def _respond(self, request: Request, data: bytes):
        self._write((request.protocol + ' ' + (request._status or '200 OK')).encode('utf-8'))
        if self._keepalive:
            request.set_header('Keep-Alive', 'timeout=' + str(self._timeout))
        if 'Content-Type' not in request._response_headers:
            request.set_header('Content-Type', 'text/plain')
        sha1 = hashlib.sha1()
        sha1.update(data)
        request.set_header('Etag', '"' + sha1.hexdigest() + '"')
        request.set_header('Date', formatdate(usegmt=True))
        request.set_header('Server', 'MiniPyP/' + __version__)
        has_body = False
        if len(data) and (request.bare or request.method != 'HEAD'):
            has_body = True
            if 'gzip' in request.headers.get('Accept-Encoding', ''):
                request.set_header('Content-Encoding', 'gzip')
                request.set_header('Vary', 'Accept-Encoding')
                data = gzip.compress(data)
        for key, value in request._response_headers.items():
            self._write((key + ': ' + value).encode('utf-8'))
        self._write(b'')
        if has_body:
            request.set_header('Content-Length', str(len(data)))
            self._write(data)

    def _write(self, data: bytes):
        self._transport.write(data + b'\r\n')


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

    def __init__(self, host='0.0.0.0', port=80, root='/var/www/html', timeout=15,
                 sites=None, handlers=None, error_pages=None, mime_types=None, directories=None):
        """
        Configure the MiniPyP server.

        :param host: the IP to bind to (0.0.0.0 for all)
        :param port: the port to bind to
        :param root: document root when no site applies
        :param timeout: default timeout for keep-alive connections
        :param sites: list of sites (see MiniPyP.add_site)
        :param handlers: dict of file handlers [extension: Handler] (see MiniPyP.add_handler)
        :param error_pages: dict of error pages {code: page}
        :param mime_types: dict of MIME types {extension: type}
        :param directories: list of directories
        """
        self._host = host
        self._port = port
        self._root = root
        self._timeout = timeout
        self._sites = sites or []
        self._handlers = handlers or {}
        self._error_pages = error_pages or {}
        self._mime_types = mime_types or {}
        self._directories = directories or {}
        self.add_handler('py', 'text/html', PyHandler())
        _default(self._error_pages, 403, {
            'html': self._error_template.format('403 Forbidden',
                                                '<p>You don\'t have permission to view this page.</p>',
                                                __version__)
        })
        _default(self._error_pages, 404, {
            'html': self._error_template.format('404 Not Found',
                                                '''<p>The requested page could not be found:</p>
        <p><code>{uri}</code></p>''',
                                                __version__)
        })
        _default(self._error_pages, 500, {
            'html': self._error_template.format('500 Internal Server Error',
                                                '''<p>An error occurred while displaying this page:</p>
        <pre>{traceback}</pre>''',
                                                __version__)
        })
        _default(self._mime_types, 'html', 'text/html')
        _default(self._mime_types, 'shtml', 'text/html')
        _default(self._mime_types, 'htm', 'text/html')
        _default(self._mime_types, 'rdf', 'application/xml')
        _default(self._mime_types, 'xml', 'application/xml')
        _default(self._mime_types, 'js', 'application/javascript')
        _default(self._mime_types, 'css', 'text/css')
        _default(self._mime_types, 'rss', 'application/rss+xml')
        _default(self._mime_types, 'mid', 'audio/midi')
        _default(self._mime_types, 'midi', 'audio/midi')
        _default(self._mime_types, 'aac', 'audio/mp4')
        _default(self._mime_types, 'm4a', 'audio/mp4')
        _default(self._mime_types, 'mp3', 'audio/mpeg')
        _default(self._mime_types, 'ogg', 'audio/ogg')
        _default(self._mime_types, 'wav', 'audio/x-wav')
        _default(self._mime_types, 'bmp', 'image/bmp')
        _default(self._mime_types, 'gif', 'image/gif')
        _default(self._mime_types, 'jpg', 'image/jpeg')
        _default(self._mime_types, 'jpeg', 'image/jpeg')
        _default(self._mime_types, 'png', 'image/png')
        _default(self._mime_types, 'svg', 'image/svg+xml')
        _default(self._mime_types, 'tif', 'image/tiff')
        _default(self._mime_types, 'tiff', 'image/tiff')
        _default(self._mime_types, 'm4v', 'video/mp4')
        _default(self._mime_types, 'mp4', 'video/mp4')
        _default(self._mime_types, 'ogv', 'video/ogg')
        _default(self._mime_types, 'mov', 'video/quicktime')
        _default(self._mime_types, 'webm', 'video/webm')
        _default(self._mime_types, 'flv', 'video/x-flv')
        _default(self._mime_types, 'wmv', 'video/x-ms-wmv')
        _default(self._mime_types, 'avi', 'video/x-msvideo')
        _default(self._mime_types, 'cur', 'image/x-icon')
        _default(self._mime_types, 'ico', 'image/x-icon')
        _default(self._mime_types, 'bin', 'application/octet-stream')
        _default(self._mime_types, 'dll', 'application/octet-stream')
        _default(self._mime_types, 'dmg', 'application/octet-stream')
        _default(self._mime_types, 'exe', 'application/octet-stream')
        _default(self._mime_types, 'img', 'application/octet-stream')
        _default(self._mime_types, 'iso', 'application/octet-stream')
        _default(self._mime_types, 'msi', 'application/octet-stream')
        _default(self._mime_types, 'safariextz', 'application/octet-stream')
        _default(self._mime_types, 'pdf', 'application/pdf')
        _default(self._mime_types, 'rtf', 'application/rtf')
        _default(self._mime_types, '7z', 'application/x-7z-compressed')
        _default(self._mime_types, 'torrent', 'application/x-bittorrent')
        _default(self._mime_types, 'crx', 'application/x-chrome-extension')
        _default(self._mime_types, 'oex', 'application/x-opera-extension')
        _default(self._mime_types, 'rar', 'application/x-rar-compressed')
        _default(self._mime_types, 'rpm', 'application/x-redhat-package-manager')
        _default(self._mime_types, 'crt', 'application/x-x509-ca-cert')
        _default(self._mime_types, 'der', 'application/x-x509-ca-cert')
        _default(self._mime_types, 'pem', 'application/x-x509-ca-cert')
        _default(self._mime_types, 'swf', 'application/x-shockwave-flash')
        _default(self._mime_types, 'xhtml', 'application/xhtml+xml')
        _default(self._mime_types, 'zip', 'application/zip')
        _default(self._mime_types, 'csv', 'text/csv')
        _default(self._mime_types, 'pl', 'applcation/perl')
        _default(self._mime_types, 'woff', 'application/font-woff')
        _default(self._mime_types, 'woff2', 'application/font-woff2')
        _default(self._mime_types, 'eot', 'application/vnd.ms-fontobject')
        _default(self._mime_types, 'ttf', 'application/x-font-ttf')
        _default(self._mime_types, 'ttc', 'application/x-font-ttf')
        _default(self._mime_types, 'otf', 'font/opentype')

    def start(self):
        """Start the server."""
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        if sys.platform == 'win32':
            asyncio.set_event_loop(asyncio.ProactorEventLoop())
        loop = asyncio.get_event_loop()
        coro = loop.create_server(lambda: Server(self), self._host, self._port)
        server = loop.run_until_complete(coro)
        sockname = server.sockets[0].getsockname()
        print('Starting MiniPyP server on ' + sockname[0] + ':' + str(sockname[1]))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop the server."""
        print('Cleaning up...')

    def add_site(self, site):
        """
        Add a site after initialization.
        :param site: dict containing 'uris' (list of hosts), and 'root' (document root)
        """
        self._sites.append(site)

    def add_handler(self, extension: str, mime_type: str, handler: Handler):
        """
        Add a file handler after initialization.
        :param extension: the file extension (e.g. 'php')
        :param mime_type: the MIME type to serve with this file
        :param handler: a Handler subclass (see Handler docs)
        """
        extension = extension.lower()
        if extension in self._handlers.keys():
            raise Exception('add_handler failed: handler already exists for .' + extension)
        self._mime_types[extension] = mime_type
        self._handlers[extension] = handler

    def get_site(self, host):
        """
        Get the site object for any given host.
        :param host: the hostname to look up
        :return: dict or None
        """
        for site in self._sites:
            if host.lower() in site['uris']:
                return site
        return None

    def get_options(self, dir: str):
        """
        Get the options for any given directory, defaulting if one is not set.
        :param dir: OS-specific directory path
        :return: dict
        """
        options = {
            'public': True,
            'static': False,
            'indexing': True,
            'dont_handle': [],
            'error_pages': self._error_pages
        }
        for path in sorted(self._directories, key=len):
            path = str(path)
            opts = self._directories[path]
            if dir.lower().startswith(path.lower()):
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
