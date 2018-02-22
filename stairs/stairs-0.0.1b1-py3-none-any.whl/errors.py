class StairsError(Exception):
    pass


class InvalidDatabase(StairsError):
    pass


class StepAlreadyEntered(StairsError):
    pass
