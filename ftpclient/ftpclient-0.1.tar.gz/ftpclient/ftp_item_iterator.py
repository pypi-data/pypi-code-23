__all__ = ["FtpItemIterator"]


class FtpItemIterator:
    def __init__(self, ftp_server):
        self.items = ftp_server.items
        self.idx = 0

    def __next__(self):
        if self.idx < len(self.items):
            result_item = self.items[self.idx]
            self.idx += 1
            return result_item
        else:
            raise StopIteration
