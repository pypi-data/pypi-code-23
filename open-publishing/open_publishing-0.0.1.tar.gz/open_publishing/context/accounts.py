from open_publishing.account import Account

class Accounts(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx
        self._refs = set() #TODO: Consider using weakref 
        
    def load(self,
             guid = None,
             account_id = None,
             fetch = True):
        if guid is None and account_id is None:
            raise TypeError('Neither guid nor account_id specified')
        elif guid is not  None and account_id is not None:
            raise TypeError('guid or account_id should be specified, nor both')
        elif guid is not None:
            account_id = Account.id_from_guid(guid)
        
        account = Account(self._ctx,
                          account_id)
        if fetch:
            account._fetch([":basic"])
        return account

    def flush(self):
        refs = self._refs.copy()
        for account in refs:
            account.flush()
        self._refs = set()

    def _add_to_changed(self,
                        database_object):
        self._refs.add(database_object)

    def _remove_from_changed(self,
                             database_object):
        if database_object in self._refs:
            self._refs.remove(database_object)
