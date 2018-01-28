from untei import constants.Const
from untei import markdown_parser.ParseResult
from datetime import datetime
from untei import utils
from untei import os


# def is_markdown(path):
#     return utils.file_type(path) == Const.FILE_TYPE_MARKDOWN

class Article:
    def __init__(self, path):


        parse_result = ParseResult(open(Const.FILES_PATH + path).read())

        self.file_type = utils.file_type(path)
        self.path = utils.file_name(path) + ".html"

        if parse_result.title == None:
            self.title = utils.file_name(path)
        else:
            self.title = parse_result.title
        self.tags = parse_result.tags
        self.authors = parse_result.authors

        if parse_result.date == None:
            modified_datetime = datetime.fromtimestamp(os.stat(Const.FILES_PATH + path).st_mtime)
            self.date = datetime.date(modified_datetime)
        else:
            self.date = parse_result.date
        self.status = parse_result.status
        self.content = parse_result.content
        self.description = "Site description will be given here"

    def is_publishable(self):
        if self.status in [ Const.STATUS_READY ]:
            return True
        elif self.status in [ Const.STATUS_DRAFT ]:
            return False
        else:
            print('Warn: Unrecognized status of file')
            print('* Status', self.status)
            print('* File', self.file_path)
            return False

    def save_to(self, directory, site_config):
        var_value_mapping = {
            Const.TEMPLATE_CONTENT_INDICATOR: self.content,
            Const.TEMPLATE_COPYRIGHT_INDICATOR: site_config.get(Const.SITE_CONFIG_KEY_COPYRIGHT),
            Const.TEMPLATE_SITE_TITLE_INDICATOR: site_config.get(Const.SITE_CONFIG_KEY_TITLE),
            Const.TEMPLATE_ARTICLE_TITLE : self.title + " - " + site_config.get("title")
        }
        content = utils.safe_apply_template(site_config.template , var_value_mapping)
        path = directory + "/" + utils.file_name(self.path) + ".html"
        f = open(path, "w")
        f.write(content)
