

class Bind(str):
    """String wrapper class to hold a loader attribute"""

    def __new__(cls, path, *args, **kwargs):
        return super().__new__(cls, path)

    def __init__(self,
                 path: str,
                 loader=None):
        """Creates a path with a loader attribute

        Attributes
        ----------
        path
            Target path
        loader
            Function to be bound to the path access action
        """
        self.loader = loader

    def action(self):
        return str(self) + '_load'

    @classmethod
    def from_action(cls, action):
        return (
            Bind(action[:-5], None)
            if action[-5:] == '_load'
            else None
        )
