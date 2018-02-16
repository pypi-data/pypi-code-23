
class Bind(str):
    """String wrapper class to hold a loader attribute
    
    Attributes
    ----------
    path: str
    loader: function
    """

    def __new__(cls, path, *args, **kwargs):
        return super().__new__(cls, path)

    def __init__(self,
                 path: str,
                 loader=None):
        """Creates a path with a loader attribute

        Attributes
        ----------
        path: str
            Target path
        loader: function
            Loader function will be called 
            the first time the path is accessed
        """
        self.path = path
        self.loader = loader

    def action(self):
        """Construct an action name from a Bind object"""
        return str(self) + '_load'

    @classmethod
    def from_action(cls, action):
        """Construct a Bind object from an action name"""
        return (
            Bind(action[:-5], None)
            if action[-5:] == '_load'
            else None
        )
