import ipaddress


class __Entry:
    """Abstract entry class."""
    commented = False

    def comment(self):
        """Comment the line."""
        self.commented = True
        return self

    def uncomment(self):
        """Uncomment the line."""
        if self.commented and self.line.startswith("# "):
            self.commented = False
        return self

    @property
    def line(self):
        """line representation in hosts file."""
        raise NotImplementedError("Create own implementation!")


class HostEntry(__Entry):
    """Host entry class."""

    def __init__(self, ip_address, canonical_name, aliases=None):
        if isinstance(ip_address, str):
            try:
                self.__ip_address = ipaddress.ip_address(ip_address)
            except ValueError:
                raise ValueError("Invalid IP address")
        elif isinstance(ip_address,
                        (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            self.__ip_address = ip_address
        else:
            raise ValueError("Invalid IP address")

        self.canonical_name = canonical_name
        if aliases:
            if not isinstance(aliases, list):
                self.aliases = aliases.split(" ")
            else:
                self.aliases = aliases
        else:
            self.aliases = []

    def __repr__(self):
        return "HostEntry <ip:{}> <name:{}>".format(
            self.ip_address,
            self.canonical_name
        )

    @property
    def line(self):
        """
        Return representation of HostEntry as one line for hosts file.

        :return: str
        """
        out = []
        width = 18
        if self.commented:
            width = 16
            out.append("#")
        out.append("{:{width}}".format(self.ip_address, width=width))
        out.append(self.canonical_name)
        if self.aliases:
            out.append(" ".join(self.aliases))
        return " ".join(out)

    @property
    def ip_address(self):
        return self.__ip_address.compressed


class CommentEntry(__Entry):
    """Comment entry class."""

    def __init__(self, comment):
        self.comment = comment

    @property
    def line(self):
        """
        Return representation of CommentEntry class for host file.
        :return: str
        """
        if self.comment.startswith("#"):
            return self.comment
        return "# {}".format(self.comment)


class BlankEntry(__Entry):
    """Blank entry class."""

    @property
    def line(self):
        return ""
