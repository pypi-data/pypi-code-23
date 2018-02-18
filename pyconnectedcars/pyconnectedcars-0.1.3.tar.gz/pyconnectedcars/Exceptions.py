class ConnectedCarsException(Exception):
    def __init__(self, message,  errors):
        super().__init__(errors)
        self.errors = errors
