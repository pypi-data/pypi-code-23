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

from buildok.reader import Reader

class FileReader(Reader):
    """File class helper to detect, create and read a certain given file.

    Attributes:
        filename (string): Path to build filename. Default is ".build".
        sample_build (string): Sample content of a build file.
    """
    READ_MODE, WRITE_MODE = "rb", "wb"
    filename = r".build"
    sample_build = r"1) Open browser `https://github.com/lexndru/buildok`!"

    def read(self):
        """Read build file content.

        Returns:
            str: Returns `filename` content on success.
            NoneType: Returns None on failure.

        Raises:
            IOError: If `filename` does not exist or does not have permissions.
        """
        with open(self.filename, self.READ_MODE) as file_:
            return [l.rstrip() for l in file_.readlines()]
        return None

    def create(self):
        """Write a sample build file with a dummy content.

        Returns:
            bool: Returns True on successful write, otherwise False.

        Raises:
            IOError: If permissions over `filename` are not enough or disk is full.
        """
        with open(self.filename, self.WRITE_MODE) as file_:
            file_.write(self.sample_build)
            return True
        return False
