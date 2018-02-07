import requests

TEMPORARY_COMPANY = 'https://api.pagar.me/1/companies/temporary'

KEYS = {}


def validate_response(pagarme_response):
    if pagarme_response.status_code == 200:
        return pagarme_response.json()
    else:
        return error(pagarme_response.json())


def create_temporary_company():
    company = requests.post(TEMPORARY_COMPANY)
    valid_company = validate_response(company)
    return valid_company


def authentication_key(api_key=None, company_temporary=False):
    global KEYS
    if company_temporary is False:
        KEYS['api_key'] = api_key
        return KEYS
    if company_temporary is True:
        company = create_temporary_company()
        api_key = company['api_key']['test']
        KEYS['api_key'] = api_key
        return KEYS


def delete(end_point, data = {}):
    data['api_key'] = KEYS['api_key']
    pagarme_response = requests.delete(end_point, json=data, headers=headers())
    return validate_response(pagarme_response)


def get(end_point, data = {}):
    data['api_key'] = KEYS['api_key']
    pagarme_response = requests.get(end_point, json=data, headers=headers())
    return validate_response(pagarme_response)


def post(end_point, data={}):
    data['api_key'] = KEYS['api_key']
    pagarme_response = requests.post(end_point, json=data, headers=headers())
    return validate_response(pagarme_response)


def put(end_point, data = {}):
    data['api_key'] = KEYS['api_key']
    pagarme_response = requests.put(end_point, json=data, headers=headers())
    return validate_response(pagarme_response)


def error(data):
    raise Exception(data['errors'])


def headers():
    _headers = {'content-type': 'application/json'}
    return _headers
