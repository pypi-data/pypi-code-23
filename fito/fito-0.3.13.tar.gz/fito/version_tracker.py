from fito import Spec, SpecField, PrimitiveField


class Version(Spec):
    spec_class = PrimitiveField(0, is_type=True)


class VersionTracker(Spec):
    data_store = SpecField(0)

    def is_tracked(self, spec_class):
        return spec_class is not Version and Version(spec_class) in self.data_store

    def get_history(self, spec_class):
        if spec_class is Version:
            return []
        else:
            return self.data_store.get_or_none(Version(spec_class)) or []

    def record_signature(self, spec_class):
        if spec_class is Version: return

        signature = spec_class.get_signature()

        history = self.get_history(spec_class)

        if history:
            last_version = history[-1]
            if last_version.diff(signature).is_empty(): return

        history.append(signature)
        self.data_store[Version(spec_class)] = history
