

class Bind(str):
    """String wrapper class to hold a loader attribute"""

    def __new__(cls, path, *args, **kwargs):
        return super().__new__(cls, path)

    def __init__(self,
                 path: str,
                 loader):
        """Creates a path with a loader attribute

        Attributes
        ----------
        path
            Target path
        loader
            Function to be bound to the path access action
        """
        self.loader = loader

