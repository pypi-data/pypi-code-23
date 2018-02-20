from sokot.configuration import SokotConfiguration


class SokotGroup():
    def __init__(self):
        self._config = SokotConfiguration()

    def add(self, name, *members):
        self._config.check()
        self._config.add_group(name, *members)
        return "Group '{}' is added: [{}]".format(name, ', '.join(members))

    def delete(self, name):
        self._config.check()
        self._config.delete_group(name)
        return "Group '{}' is deleted".format(name)

    def ls(self):
        return self._config.list_group()
