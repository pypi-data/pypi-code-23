from sigauth import utils


SECRET = 'super-duper-secret'


def test_signer_without_body():
    signer = utils.RequestSigner(secret=SECRET)

    headers = signer.get_signature_headers(
        url='http://e.co/',
        body='',
        method='POST',
        content_type='application/json'
    )

    assert 'id="directory' in headers[signer.header_name]


def test_signer_with_body():
    signer = utils.RequestSigner(secret=SECRET)

    headers = signer.get_signature_headers(
        url='http://e.co/',
        body='content',
        method='POST',
        content_type='application/json'
    )

    assert 'id="directory' in headers[signer.header_name]


def test_request_signer_passes_correct_secret_to_signer(settings):
    signer = utils.RequestSigner(secret=SECRET)

    assert signer.secret == SECRET


def test_get_path_with_querystring():
    assert utils.get_path('http://e.co/?thing=1') == '/?thing=1'


def test_get_path_without_querystring():
    assert utils.get_path('http://e.co/aa/') == '/aa/'
