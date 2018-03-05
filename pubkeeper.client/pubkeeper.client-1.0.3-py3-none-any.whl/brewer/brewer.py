"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.topic import Topic


class Brewer(Topic):
    def get_config(self):  # pragma: no cover
        raise NotImplementedError()

    def new_patrons(self, patrons):  # pragma: no cover
        raise NotImplementedError()

    def remove_patron(self, patron_id):  # pragma: no cover
        raise NotImplementedError()

    def brew(self, data):  # pragma: no cover
        raise NotImplementedError()
