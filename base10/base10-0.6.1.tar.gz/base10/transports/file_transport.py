from base10.base import Reader, Writer
from base10.exceptions import TransportError


class FileTransport(object):
    def __init__(self, filename, mode):
        try:
            self._file = open(filename, mode)
        except IOError as e:
            raise TransportError('Could not open file "{}"'.format(filename), e)


class FileReader(FileTransport, Reader):
    def __init__(self, filename, mode='r'):
        super(FileReader, self).__init__(filename, mode)

    def read(self):
        for line in self._file:
            yield line


class FileWriter(FileTransport, Writer):
    def __init__(self, filename, mode='w'):
        super(FileWriter, self).__init__(filename, mode)

    def write(self, string):
        self._file.write(string + '\n')
        return True
