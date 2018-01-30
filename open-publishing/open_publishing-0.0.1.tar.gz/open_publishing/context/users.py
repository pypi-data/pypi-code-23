from open_publishing.user import User
from open_publishing.core.enums import UsersSearchType

class Users(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx
        self._refs = set() #TODO: Consider using weakref 
        
    def load(self,
             guid = None,
             user_id = None,
             email = None,
             fetch = True):
        if guid is not None and user_id is None and email is None:
            user_id = User.id_from_guid(guid)
        elif user_id is not None and guid is None and email is None:
            user_id = user_id
        elif email is not None and guid is None and user_id is None:
            user_id = self._ctx.gjp.resolve_email(email)['user_id']
        else:
            raise TypeError('guid, user_id OR email should be specified')
        
        user = User(self._ctx,
                    user_id)
        if fetch:
            user._fetch([":basic"])
        return user
        
    def create(self,
               first_name,
               last_name,
               email):
        user_id = self._ctx.gjp.create_user(first_name=first_name,
                                        last_name=last_name,
                                        email=email)
        
        user = User(self._ctx,
                    user_id)
        user._fetch([":basic"])
        with user:
            user.address.country = "DEU"
            user.statement.statement_mail = False
            user.statement.generate_statement = True
        return user

    def flush(self):
        refs = self._refs.copy()
        for user in refs:
            user.flush()
        self._refs = set()

    def _add_to_changed(self,
                        database_object):
        self._refs.add(database_object)

    def _remove_from_changed(self,
                             database_object):
        if database_object in self._refs:
            self._refs.remove(database_object)

    def search(self,
               query = None,
               search_type = UsersSearchType.email):
        res = self._ctx.gjp.users_search(query=query,
                                         search_type=search_type)
        guids = [ obj["GUID"] for obj in res ]
        users = [self.load(guid=guid, fetch=False) for guid in guids]
        return users
