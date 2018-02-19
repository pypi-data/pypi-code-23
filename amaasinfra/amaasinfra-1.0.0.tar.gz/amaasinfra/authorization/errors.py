class AuthorizationError(Exception):
    """Raised when a user is requesting a resource that she does not have access to."""
    _msg = 'Access to requested resource is denied'

    def __str__(self):
        return self._msg.format(**vars(self))

class AmidAuthorizationError(AuthorizationError):
    """Raised when a user is requesting an asset manager resource that she does not have access to."""
    _msg = ('{user.username} ({user.asset_manager_id}) is not permissed for {asset_manager_id}')
    
    def __init__(self, user, asset_manager_id):
        self.asset_manager_id = (','.join([str(amid) for amid in asset_manager_id]) 
                                 if isinstance(asset_manager_id, list)
                                 else str(asset_manager_id))
        self.user = user

class BookAuthorizationError(AuthorizationError):
    """Raised when a user is requesting an asset manager book that she does not have sufficient access to."""
    _msg = ('{access} access to asset manager {asset_manager_id}, book {book_id} '
            'is denied for {user.username} ({user.asset_manager_id})')

    def __init__(self, user, asset_manager_id, book_id, access):
        self.asset_manager_id = asset_manager_id
        self.user = user
        self.book_id = book_id
        self.access = access