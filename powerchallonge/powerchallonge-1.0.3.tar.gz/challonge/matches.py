from challonge import tools
prefix = 'match'


def index(identifier, **params):
    api_method = 'Matches : Index'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches'
    return tools.request('GET', target, api_method, prefix, 0, **params)


def show(identifier, match_id, **params):
    api_method = 'Matches  : Show'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id)
    return tools.request('GET', target, api_method, prefix, 0, **params)


def update(identifier, match_id, **params):
    api_method = 'Matches  : Update'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id)
    return tools.request('PUT', target, api_method, prefix, 1, **params)


def reopen(identifier, match_id):
    api_method = 'Matches  : Reopen'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id) + '/reopen'
    return tools.request('POST', target, api_method, prefix, 0)
