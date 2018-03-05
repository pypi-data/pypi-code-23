from sigauth.middleware import SignatureCheckMiddlewareBase
from sigauth.utils import RequestSigner


SECRET = 'super secret'
SENDER_ID = 'test sender'


class SignatureRejectionMiddleware(SignatureCheckMiddlewareBase):
    secret = SECRET


def test_signature_rejection_rejects_missing_signature(rf):
    request = rf.get('/')

    response = SignatureRejectionMiddleware().process_request(request)

    assert response.status_code == 401


def test_signature_rejection_rejects_invalid_signature(rf):

    request = rf.get('/', HTTP_X_SIGNATURE='NOT-CORRECT', CONTENT_TYPE='')

    response = SignatureRejectionMiddleware().process_request(request)

    assert response.status_code == 401


def test_signature_rejection_accepts_valid_signature(rf, settings):
    # in practive the signature is generated on the server making the request.
    # on the requesting server, it will know the shared secret
    signer = RequestSigner(secret=SECRET)

    headers = signer.get_signature_headers(
        url='/',
        body='',
        method='GET',
        content_type=''
    )

    request = rf.get(
        '/',
        HTTP_X_SIGNATURE=headers[signer.header_name],
        CONTENT_TYPE='',
    )

    response = SignatureRejectionMiddleware().process_request(request)

    assert response is None


def test_signature_check_skipped(rf, settings):
    settings.URLS_EXCLUDED_FROM_SIGNATURE_CHECK = ['/']
    request = rf.get('/')

    response = SignatureRejectionMiddleware().process_request(request)

    assert response is None
