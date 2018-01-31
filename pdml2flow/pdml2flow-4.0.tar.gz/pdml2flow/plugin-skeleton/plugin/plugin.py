# vim: set fenc=utf8 ts=4 sw=4 et :
from os import environ
from pdml2flow.plugin import Plugin1

CONFIGURATION = environ.get('CONFIGURATION', 'default value')

class Plugin(Plugin1):
    """Version 1 plugin interface."""

    def flow_new(self, flow, frame):
        """Called every time a new flow is opened."""
        pass

    def flow_expired(self, flow):
        """Called every time a flow expired, before printing the flow."""
        pass

    def flow_end(self, flow):
        """Called every time a flow ends, before printing the flow."""
        pass

    def frame_new(self, frame, flow):
        """Called for every new frame."""
        pass

