class Me(object):
    def __init__(self,
                 context):
        res = context.gjp.get_me()
        self._user_name = res['user_name']
        self._user_id = res['user_id']
        self._realm_name = res['realm_name']
        self._realm_id = res['realm_id']

    @property
    def user_name(self):
        return self._user_name

    @property
    def user_id(self):
        return self._user_id

    @property
    def user_guid(self):
        return 'user.{0}'.format(self._user_id)
    
    @property
    def realm_name(self):
        return self._realm_name

    @property
    def realm_id(self):
        return self._realm_id
