from datetime import datetime
import hashlib
import xmltodict
import os
import requests
import re
import random

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BASE_AUTH_XML_FILE = '/realex/realex_files/auth.xml'
_BASE_3DS_VERIFY_ENROLLED_XML_FILE = '/realex/realex_files/3ds_verify_enrolled.xml'
_BASE_3DS_VERIFY_SIGNED_XML_FILE = '/realex/realex_files/3ds_verify_signed.xml'
_ORDERID_LENGTH = 13


class Realex:
    SHARED_SECRET = None
    AUTH_URL = "https://api.realexpayments.com/epage-remote.cgi"
    MERCHANT_ID = None
    VERIFY_SIGNED_URL = "https://api.realexpayments.com/epage-remote.cgi"
    VERIFY_ENROLLED_URL = "https://api.realexpayments.com/epage-remote.cgi"
    CALLBACK_URL = None

    @classmethod
    def create_charge(cls, amount, currency, card_holder_name, card_number, cvv, expiry_month, expiry_year, card_type,
                      cavv=None, xid=None, eci=None):
        order_id = _generate_order_id()
        timestamp = _generate_time_stamp()
        card_number = _remove_white_space(card_number)
        amount = _remove_decimal_places(amount)
        sha1hash = _generate_sha1hash(timestamp, cls.MERCHANT_ID, order_id, amount, currency, card_number,
                                      cls.SHARED_SECRET)

        response = requests.post(cls.AUTH_URL,
                                 data=_generate_xml_data(_BASE_AUTH_XML_FILE,
                                                         amount,
                                                         currency,
                                                         order_id,
                                                         timestamp,
                                                         sha1hash,
                                                         card_holder_name,
                                                         card_number=card_number,
                                                         expiry_month=expiry_month,
                                                         expiry_year=expiry_year,
                                                         card_type=card_type,
                                                         merchant_id=cls.MERCHANT_ID,
                                                         cvv=cvv,
                                                         cavv=cavv,
                                                         xid=xid,
                                                         eci=eci),
                                 headers=_generate_basic_xml_headers())
        return _parse_create_charge_response(response)

    @classmethod
    def verify_enrolled(cls, amount, currency, card_holder_name, card_number, expiry_month, expiry_year, card_type):
        order_id = _generate_order_id()
        timestamp = _generate_time_stamp()
        card_number = _remove_white_space(card_number)
        amount = _remove_decimal_places(amount)
        sha1hash = _generate_sha1hash(timestamp, cls.MERCHANT_ID, order_id, amount, currency, card_number,
                                      cls.SHARED_SECRET)

        response = requests.post(cls.VERIFY_ENROLLED_URL,
                                 data=_generate_xml_data(_BASE_3DS_VERIFY_ENROLLED_XML_FILE,
                                                         amount,
                                                         currency,
                                                         order_id,
                                                         timestamp,
                                                         sha1hash,
                                                         card_holder_name=card_holder_name,
                                                         card_number=card_number,
                                                         expiry_month=expiry_month,
                                                         expiry_year=expiry_year,
                                                         card_type=card_type,
                                                         merchant_id=cls.MERCHANT_ID),
                                 headers=_generate_basic_xml_headers())

        return _parse_verify_enrolled_response(response, order_id, sha1hash)

    @classmethod
    def redirect_to_secure_site(cls, third_party_url, pareq, merchant_data, request_id):
        return requests.post(third_party_url,
                             data={'PaReq': pareq,
                                   'termUrl': cls.CALLBACK_URL,
                                   'MD': merchant_data,
                                   'ApiKey': cls.MERCHANT_ID,
                                   'RequestId': request_id},
                             headers=_generate_basic_xml_headers())

    @classmethod
    def verify_signed(cls, amount, currency, pares, order_id):
        timestamp = _generate_time_stamp()
        amount = _remove_decimal_places(amount)
        sha1hash = _generate_sha1hash(timestamp, cls.MERCHANT_ID, order_id, amount, currency, "", cls.SHARED_SECRET)
        response = requests.post(cls.VERIFY_SIGNED_URL,
                                 data=_generate_xml_data(_BASE_3DS_VERIFY_SIGNED_XML_FILE,
                                                         amount,
                                                         currency,
                                                         order_id,
                                                         timestamp,
                                                         sha1hash,
                                                         pares=pares,
                                                         merchant_id=cls.MERCHANT_ID),
                                 headers=_generate_basic_xml_headers())

        return _parse_verify_signed_response(response)


def _parse_verify_signed_response(response):
    if response.status_code != 200:
        raise Exception(response.request.url + ' returned ' 'status_code=' + str(response.status_code))

    untangled_response = extract_xml_response(response)

    return {'status_code': response.status_code,
            'cavv': untangled_response['threedsecure']['cavv'],
            'eci': untangled_response['threedsecure']['eci'],
            'xid': untangled_response['threedsecure']['xid'],
            'message': untangled_response['message'],
            'realex_result_code': untangled_response['result'],
            'status': untangled_response['threedsecure']['status']}


def _parse_verify_enrolled_response(response, order_id, sha1hash):
    if response.status_code != 200:
        raise Exception(response.request.url + ' returned ' 'status_code=' + str(response.status_code))

    untangled_response = extract_xml_response(response)

    return {'status_code': response.status_code,
            'realex_result_code': untangled_response['result'],
            'message': untangled_response['message'],
            'pareq': untangled_response['pareq'],
            'url': untangled_response['url'],
            'enrolled': untangled_response['enrolled'],
            'order_id': order_id,
            'sha1hash': sha1hash}


def _generate_xml_data(base_xml, amount, currency, order_id, timestamp, sha1hash, card_holder_name=None,
                       card_number=None, expiry_month=None, expiry_year=None, card_type=None, merchant_id=None,
                       cvv=None, cavv=None, xid=None, eci=None, pares=None):
    untangled_xml = _get_untangled_base_xml(base_xml)

    untangled_xml['request']['sha1hash'] = sha1hash
    untangled_xml['request']['orderid'] = order_id
    untangled_xml['request']['@timestamp'] = timestamp
    untangled_xml['request']['amount']['#text'] = amount
    untangled_xml['request']['amount']['@currency'] = currency

    if card_number:
        untangled_xml['request']['card']['number'] = card_number
    if card_holder_name:
        untangled_xml['request']['card']['chname'] = card_holder_name
    if expiry_month and expiry_year:
        untangled_xml['request']['card']['expdate'] = expiry_month + expiry_year
    if card_type:
        untangled_xml['request']['card']['type'] = card_type
    if merchant_id:
        untangled_xml['request']['merchantid'] = merchant_id
    if pares:
        untangled_xml['request']['pares'] = pares
    if cvv:
        untangled_xml['request']['card']['cvn']['number'] = cvv
    if cavv:
        untangled_xml['request']['mpi']['cavv'] = cavv
    if xid:
        untangled_xml['request']['mpi']['xid'] = xid
    if eci:
        untangled_xml['request']['mpi']['eci'] = cavv

    return _convert_to_xml(untangled_xml)


def _parse_create_charge_response(response):
    if response.status_code != 200:
        raise Exception(response.request.url + ' returned ' 'status_code=' + str(response.status_code))

    realex_result_code = extract_xml_response(response)['result']
    message = extract_xml_response(response)['message']

    if realex_result_code == '00':
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code, 'message': 'SUCCESS'}
    elif realex_result_code == '101':
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code,
                'message': message}
    elif re.search(r'^10[2,3,7]', realex_result_code):
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code, 'message': 'DECLINED'}
    elif re.search(r'^2[0-9][0-9]', realex_result_code):
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code, 'message': 'BANK_ERROR'}
    elif re.search(r'^3[0-9][0-9]', realex_result_code):
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code,
                'message': 'REALEX_ERROR'}
    elif re.search(r'^5[0-9][0-9]', realex_result_code):
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code,
                'message': message}
    elif re.search(r'^60[0,1,3]', realex_result_code):
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code, 'message': 'ERROR'}
    elif realex_result_code == '666':
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code,
                'message': 'CLIENT_DEACTIVATED'}
    else:
        return {'status_code': response.status_code, 'realex_result_code': realex_result_code, 'message': 'NOT FOUND'}


def extract_xml_response(custom_response):
    return xmltodict.parse(custom_response.content)['response']


def _generate_order_id():
    return _generate_random_alphanumeric_string(_ORDERID_LENGTH)


def _generate_sha1hash(timestamp, merchant_id, orderid, amount, currency, card_number, shared_secret):
    initial_sha1_hash = hashlib.sha1((timestamp + "." + merchant_id + "." + orderid + "." + amount + "." + currency + "." + card_number)
                                     .encode('utf-8')).hexdigest()

    return hashlib.sha1((initial_sha1_hash + "." + shared_secret).encode('utf-8')).hexdigest()


def _generate_time_stamp():
    return "{:%Y%m%d%H%M%S}".format(datetime.now())


def _get_untangled_base_xml(base_file):
    with open(_BASE_DIR + base_file) as fd:
        return xmltodict.parse(fd.read())


def _convert_to_xml(untangled_xml):
    return xmltodict.unparse(untangled_xml, full_document=False)


def _remove_decimal_places(number):
    return str(int(float(number) * 100))


def _generate_random_alphanumeric_string(length):
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(length))


def _remove_white_space(param):
    return param.replace(" ", "")


def _generate_basic_xml_headers():
    return {'Content-Type': 'application/html'}
