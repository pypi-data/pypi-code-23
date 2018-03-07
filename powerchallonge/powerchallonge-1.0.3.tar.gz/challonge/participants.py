from challonge import tools
prefix = 'participant'


def index(identifier):
    api_method = 'Participants : Index'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants'
    return tools.request('GET', target, api_method, prefix, 0)


def create(identifier, **params):
    api_method = 'Participants : Create'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants'
    return tools.request('POST', target, api_method, prefix, 1, **params)


def bulk_add(identifier, **params):
    api_method = 'Participants : Bulk Add'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants/bulk_add'
    return tools.request('POST', target, api_method, 'participants[]', 1,
                         **params)


def show(identifier, participant_id, **params):
    api_method = 'Participants : Show'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants/' + str(participant_id)
    return tools.request('GET', target, api_method, prefix, 0, **params)


def update(identifier, participant_id, **params):
    api_method = 'Participants : Update'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants/' + str(participant_id)
    return tools.request('PUT', target, api_method, prefix, 1, **params)


def check_in(identifier, participant_id):
    api_method = 'Participants : Check In'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants/' + \
        str(participant_id) + '/check_in'
    return tools.request('POST', target, api_method, prefix, 0)


def undo_check_in(identifier, participant_id):
    api_method = 'Participants : Undo Check In'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants/' + \
        str(participant_id) + '/undo_check_in'
    return tools.request('POST', target, api_method, prefix, 0)


def destroy(identifier, participant_id):
    api_method = 'Participants : Destroy'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants/' + str(participant_id)
    return tools.request('DELETE', target, api_method, prefix, 0)


def randomize(identifier):
    api_method = 'Participants : Randomize'
    identifier = tools.convert_identifier(identifier)
    target = '/' + identifier + '/participants/randomize'
    return tools.request('POST', target, api_method, prefix, 0)
