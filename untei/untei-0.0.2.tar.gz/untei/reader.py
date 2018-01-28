import constants
import markdown_parser

const = constants.const()

class FileReader:
    def __init__(self, **kwargs):
        self.status = kwargs[const.STATUS]
        self.file_type = kwargs[const.FILE_TYPE]
        self.file_path = kwargs[const.FILE_PATH]

    def isPublishable(self):
        if self.status in [ const.STATUS_READY ]:
            return True
        elif self.status in [ const.STATUS_DRAFT ]:
            return False
        else:
            print('Warn: Unrecognized status of file')
            print('* Status', self.status)
            print('* File', self.file_path)
            return False

    def plain_content(self):
        return open(self.file_path).read()


    def create_content(self):
        if self.file_type == const.FILE_TYPE_MARKDOWN:
            return markdown_parser.parse(self.plain_content())
        else:
            return self.plain_content()
