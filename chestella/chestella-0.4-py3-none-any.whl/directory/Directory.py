import os

class Directory():
    def __init__(self, path):
        self.path = path

        try:
            os.makedirs(self.path)
        except OSError as e:
            raise

    def write_file(self, path, content):
        with open("{}/{}".format(self.path, path), 'w') as f:
            f.write(content)
