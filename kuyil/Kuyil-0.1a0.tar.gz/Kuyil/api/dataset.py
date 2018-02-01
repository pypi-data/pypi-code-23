
class Dataset():

    def __init__(self, dataset_class, instance, label, repository, comment=None,
                 metadata=None):
        self.instance = instance
        self.dataset_class = dataset_class
        self.label = label
        self.repository = repository
        self.comment = comment
        self.metadata = metadata


    def get_write_lock_if_idle(self):
        print()

    def maintain_write_lock(self, pid):
        print()

    def write_failed(self, pid, comment=None):
        print()

    def write_success(self, pid, comment=None):
        print()