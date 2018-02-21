
class FileData(object):
    def __init__(self, logical_path, physical_path, methods, lines, hash):
        self.logicalPath = logical_path
        self.physicalPath = physical_path
        self.methods = methods
        self.lines = lines
        self.hash = hash
        self.error = None


class FileDataWithCommits(FileData):
    def __init__(self, file_data, commits_per_file, git_path):
        super(FileDataWithCommits, self).__init__(file_data.logical_path, git_path, file_data.methods, file_data.lines, file_data.hash)
        self.commitIndexes = commits_per_file
