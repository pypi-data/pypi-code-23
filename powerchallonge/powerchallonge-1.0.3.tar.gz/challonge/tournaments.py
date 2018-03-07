from challonge import tools
prefix = 'tournament'


def index(**params):
    api_method = 'Tournaments : Index'
    return tools.request('GET', '', api_method, prefix, 0, ** params)


def create(**params):
    api_method = 'Tournaments : Create'
    return tools.request('POST', '', api_method, prefix, 1, **params)


def show(identifier, **params):
    api_method = 'Tournaments : Show'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier
    return tools.request('GET', target, api_method, prefix, 0, **params)


def update(identifier, **params):
    api_method = 'Tournaments : Update'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier
    return tools.request('PUT', target, api_method, prefix, 1, **params)


def destroy(identifier):
    api_method = 'Tournaments : Destroy'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier
    return tools.request('DELETE', target, api_method, prefix, 0)


def process_check_ins(identifier, **params):
    api_method = 'Tournaments : Process Check-ins'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/process_check_ins'
    return tools.request('POST', target, api_method, prefix, 0, **params)


def abort_check_in(identifier, **params):
    api_method = 'Tournaments : Abort Check-in'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/abort_check_in'
    return tools.request('POST', target, api_method, prefix, 0, **params)


def start(identifier, **params):
    api_method = 'Tournaments : Start'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/start'
    return tools.request('POST', target, api_method, prefix, 0, **params)


def finalize(identifier, **params):
    api_method = 'Tournaments : Finalize'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/finalize'
    return tools.request('POST', target, api_method, prefix, 0, **params)


def reset(identifier, **params):
    api_method = 'Tournaments : Reset'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/reset'
    return tools.request('POST', target, api_method, prefix, 0, **params)
