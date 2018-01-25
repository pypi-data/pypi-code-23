import os
from fito import Spec, PrimitiveField
from fito.version_tracker import VersionTracker


class GlobalConfig(Spec):
    enable_version_tracker = PrimitiveField(default=False)

    @property
    def version_tracker(self):
        if not self.enable_version_tracker: return

        # lazy import to avoid dependency loops
        from fito.data_store import FileDataStore
        return VersionTracker(
            FileDataStore(
                os.path.join(os.getenv('HOME'), '.fito/version_tracker'),
                get_cache_size=100
            )
        )




fito_rc_fname = os.path.join(os.getenv("HOME"), '.fitorc.yaml')
if os.path.exists(fito_rc_fname):
    global_config = GlobalConfig.from_yaml().load(fito_rc_fname)
else:
    global_config = GlobalConfig()

