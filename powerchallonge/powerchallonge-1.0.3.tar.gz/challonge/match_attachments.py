from challonge import tools
prefix = 'match_attachment'


def index(identifier, match_id):
    api_method = 'Match Attachments : Index'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id) + '/attachments'
    return tools.request('GET', target, api_method, prefix, 0)


def create(identifier, match_id, **params):
    api_method = 'Match Attachments : Create'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id) + '/attachments'
    return tools.request('POST', target, api_method, prefix, 1,
                         **params)


def show(identifier, match_id, attachment_id):
    api_method = 'Match Attachments : Show'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id) + '/attachments/'\
        + str(attachment_id)
    return tools.request('GET', target, api_method, prefix, 0)


def update(identifier, match_id, attachment_id, **params):
    api_method = 'Match Attachments : Update'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id) + '/attachments/'\
        + str(attachment_id)
    return tools.request('PUT', target, api_method, prefix, 1,
                         **params)


def destroy(identifier, match_id, attachment_id):
    api_method = 'Match Attachments : Destroy'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/matches/' + str(match_id) + '/attachments/'\
        + str(attachment_id)
    return tools.request('DELETE', target, api_method, prefix, 0)
