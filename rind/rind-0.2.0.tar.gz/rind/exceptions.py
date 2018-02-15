class RindError(Exception):
    pass


class MultiContainersFoundError(RindError):
    pass


class ContainerNotRunning(RindError):
    pass
