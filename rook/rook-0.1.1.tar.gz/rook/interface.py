"""This is the external interface to the Rook package."""

# FUTURE - convert dcostring to restructured text


class Rook(object):
    """This class represents a control object for the module."""

    def __init__(self):
        """Initialize a new Rook controller."""
        import rook.singleton

        self._rook = rook.singleton.singleton_obj

    def start(self, host=None, port=None):
        """Start the rook module.

        Arguments:
        host - The address to the Rookout Agent. Only "localhost" is recommended.
        port - The port the Rookout Agent is listening on.
        """
        return self._rook.connect(host, port)

    def set_version_information(self, **kwargs):
        """Set the application's version information.

        If the agent connection has already been established, updated version information will be sent immediately.
        If the agent connection has not yet been established, the version information will be sent on connection.
        """
        self._rook.set_version_information(**kwargs)

    def collect_data(self, description, send_by_default=True, **kwargs):
        """Collect application data at this line.

        collect_data causes the following chain of events:
        - a data collection event is trigger based on the given description.
        - If there are Augs registered on this event:
            - Augs are provdided with the key word arguments are are executed.
        - If there are no Augs registered on this event:
            - If send_by_default is True a default Aug is created that sends a basic monitor message with the
                description and the key word arguments home.
            - If send_by_default is False nothing happens.
        """
        raise NotImplementedError()
        self._rook.collect_data(description, send_by_default, kwargs)
