import ipaddress
import re

from hostsctl.entries import BlankEntry, CommentEntry, HostEntry


# TODO check if it is possible do actions with only 2 modes (read/write)


class HostController(object):
    def __init__(self, path='/etc/hosts', mode='r'):
        self.content = []
        # TODO check if file exists
        # TODO check if is readable and writeable
        # TODO add mode read/write
        import os
        path = os.path.expanduser(path)
        parent_dir = os.path.dirname(path)

        if not os.path.exists(parent_dir):
            # TODO parent directory is not exists
            pass

        if not os.path.exists(path) and mode == "r":
            # TODO we want read but file does not exists
            pass

        self.path = path

        if mode in ("r", "w"):
            self.mode = mode
        else:
            raise AttributeError("Invalid mode")

        self.load()

    def load(self):
        # load file content
        with open(self.path, "r") as file:
            for line in file.readlines():
                line = line.strip()
                self.__parse_line(line)

    def populate(self):
        # write to file
        with open(self.path, self.mode) as file:
            for entry in self.content:
                file.write("{}\n".format(entry.line))

    def add(self, entry):
        self.content.append(entry)

    def remove(self, entry):
        self.content.remove(entry)

    def find(self, value):
        try:
            ipaddress.ip_address(value)
            for entry in self.content:
                if isinstance(entry, HostEntry) and entry.ip_address == value:
                    return entry
        except ValueError:
            for entry in self.content:
                if isinstance(entry, HostEntry):
                    if entry.canonical_name == value:
                        return entry

    def list(self):
        return self.content

    @property
    def size(self):
        return len(self.content)

    def __parse_line(self, line):
        line_regex = re.compile(
            r'^(\S+)[\ \t]*(\S+)[\ \t]*([a-zA-Z0-9\-\ \.\t]*)$'
        )
        if line.startswith("#"):
            comment = CommentEntry(line[1:])
            self.content.append(comment)
        elif line:
            match = line_regex.match(line)
            if match:
                address, canonical_name, aliases = match.groups()
                try:
                    entry = HostEntry(address, canonical_name, aliases)
                except ValueError:
                    print("ERR!!!")
                else:
                    self.content.append(entry)
        elif not line:
            blank = BlankEntry()
            self.content.append(blank)
        else:
            raise ValueError("Invalid input")
