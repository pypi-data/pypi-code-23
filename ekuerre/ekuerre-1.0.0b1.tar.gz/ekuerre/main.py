from io import BytesIO
from urlparse import parse_qs
import qrcode


def application(environ, start_response):
    path = environ['PATH_INFO']
    if path.startswith('/qr.png'):
        params = parse_qs(environ['QUERY_STRING'])
        data = params.get('data', [None])[0]
        code = qrcode.QRCode()
        code.add_data(data)
        code.make(fit=True)
        image = code.make_image()
        the_bytes = BytesIO()
        image.save(the_bytes)

        headers = [
            ('Content-Type', 'image/png'),
        ]
        start_response('200 OK', headers)
        return [the_bytes.getvalue()]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('', 32491, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped")