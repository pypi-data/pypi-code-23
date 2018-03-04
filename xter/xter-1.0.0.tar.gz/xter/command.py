class Command:
    name = ''
    parameters = []

    def is_valid(self):
        return self.name != ''

