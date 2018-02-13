class GPMItem:

    def __init__(self, item):
        self.item = item

    def get(self, field, default = None):
        return self.item.get(field, default)
