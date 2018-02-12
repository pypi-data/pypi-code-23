# Copyright 2018 Alexandru Catrina
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

class Reader(object):
    """Reader wrapper to gather build steps.

    A new instance registers a new reader.
    Has support for `.build` files and `README.md` files.

    Attributes:
        readers (list): A list of all registered readers.
        reader (str): Reader class name.
        filename (str): File name of the file to read.
        filepath (str): File path of the file to read.
    """
    readers = []
    reader = ""
    filename = ""
    filepath = ""

    def __init__(self):
        self.readers.append(self)
        self.reader = self.__class__.__name__
        self.patch_filename()

    def patch_filename(self):
        """Apply a patch to filename if filepath is set.

        Returns:
            self: Reader instance.
        """
        if self.filepath == "":
            return self
        if os.path.isfile(self.filepath):
            self.filename = self.filepath
        elif os.path.isdir(self.filepath):
            self.filename = r"{}/{}".format(self.filepath, self.filename)
        return self

    def read(self):
        """Read build file content.

        Raises:
            NotImplementedError: Readers must implement this method.
        """
        raise NotImplementedError("%s must implement read method" % self.reader)

    def exists(self):
        """Check if build file exists.

        Returns:
            bool: Returns True if `filename` exists, otherwise False.
        """
        return os.path.isfile(self.filename)

    @classmethod
    def get_all(cls):
        """Return all build steps from all sources.

        Raises:
            ValueError: If no reader was initialized.

        Returns:
            tuple: Non-empty tuple of build steps.
        """
        if len(cls.readers) == 0:
            raise ValueError("No reader initialized")
        data = []
        for r in cls.readers:
            data += r.read()
        return tuple(data)

    @classmethod
    def get_first(cls):
        """Return all build steps from first source.

        Raises:
            ValueError: If no reader was initialized.

        Returns:
            tuple: Non-empty tuple of build steps.
        """
        try:
            data = cls.readers[0].read()
        except IndexError:
            raise ValueError("No reader initialized")
        return tuple([d for d in data if d])
