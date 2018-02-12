from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.core.amaas_model import AMaaSModel


class Reference(AMaaSModel):

    def __init__(self, reference_value, reference_primary=False, *args, **kwargs):
        self.reference_value = reference_value
        self.reference_primary = reference_primary
        super(Reference, self).__init__(*args, **kwargs)

    @property
    def reference_primary(self):
        if hasattr(self, '_reference_primary'):
            return self._reference_primary

    @reference_primary.setter
    def reference_primary(self, value):
        """
        Always convert to bool if the service/database returns 0 or 1
        """
        if value is not None:
            self._reference_primary = True if value else False