from constants import Const
import utils
import sys
import os
from distutils import dir_util
import shutil
import article
import interfaces
theme_path = Const.FILES_PATH + 'theme'
sys.path.append(theme_path)


def read_config(path):
    config = {}

    config_lines = open(path).readlines()
    for l in config_lines:
        if not(l.startswith("#")):
            key, value = l.split(" = ")
            if is_config_key(key):
                config[key] = value
            else:
                print("Warn: Unknown key '" + key + "'")
        else:
            pass
    return config

def is_config_key(key):
    return key in Const.SITE_CONFIG_KEYS


class SiteConfig:
    def __init__(self, path):
        self.config = read_config(path)
        self.tags_to_article = {}
        self.authors_to_article = {}
        self.output_path = Const.OUTPUT_DIRECTORY
        self.template = open(Const.TEMPLATE_ARTICLE).read()
        self.articles_ordered_by_date = []

    def all_articles(self):
        return self.articles_ordered_by_date

    def get(self, key):
        return self.config[key]

    def add_articles(self, files):
        articles = []
        for f in files:
            if utils.file_type(f) == Const.FILE_TYPE_MARKDOWN:
                try:
                    a = article.Article(f)
                except:
                    print("Parse Error: " + f)
                articles.append(a)
                self.__update_tags_by_article__(a)
            else:
                pass

        self.articles_ordered_by_date = utils.order_articles_by_date(articles)

    def __update_tags_by_article__(self, a):
        for tag in a.tags:
            if tag in self.tags_to_article.keys():
                self.tags_to_article[tag].append(a)
            else:
                self.tags_to_article[tag] = [ a ]

    def __provide_interface_for_tag__(self, tag):
        variables = {
            "articles_tagged_as": self.tags_to_article[tag],
            "current_tag"       : tag
        }
        return variables

    def create_tag_pages(self):
        for tag in self.tags_to_article.keys():
            src = open(Const.SITE_CONFIG_TAG).read()

            interface = interfaces.tag_interface(self, tag)

            exec(src, interface, interface)
            var_value_mapping = {
                Const.TEMPLATE_CONTENT_INDICATOR: interface["body"],
                Const.TEMPLATE_SITE_TITLE_INDICATOR: self.config[Const.SITE_CONFIG_KEY_TITLE],
                Const.TEMPLATE_COPYRIGHT_INDICATOR: self.config[Const.SITE_CONFIG_KEY_COPYRIGHT],
                Const.TEMPLATE_ARTICLE_TITLE : "Tag: " + tag + " - " + self.config["title"]
            }
            content = utils.safe_apply_template(self.template , var_value_mapping)
            path = self.output_path + "/" + tag + ".html"
            with open(path, "w") as f:
                f.write(content)

    def copy_theme_files(self):
        files = os.listdir(theme_path)
        for f_name in files:
            f = theme_path + "/" + f_name

            if not(utils.is_uncopied(f_name)):
                if os.path.isdir(f):
                    dir_util.copy_tree(f, Const.OUTPUT_DIRECTORY + f_name)
                else:
                    shutil.copy2(f, Const.OUTPUT_DIRECTORY + f_name)

    def create_index_page(self):
        src = open(Const.SITE_CONFIG_INDEX).read()

        interface = interfaces.index_interface(self)

        exec(src, interface, interface)
        var_value_mapping = {
            Const.TEMPLATE_CONTENT_INDICATOR: interface["body"],
            Const.TEMPLATE_SITE_TITLE_INDICATOR: self.config[Const.SITE_CONFIG_KEY_TITLE],
            Const.TEMPLATE_COPYRIGHT_INDICATOR: self.config[Const.SITE_CONFIG_KEY_COPYRIGHT],
            Const.TEMPLATE_ARTICLE_TITLE : self.config["title"]
        }
        content = utils.safe_apply_template(self.template , var_value_mapping)

        path = self.output_path + "/index.html"

        with open(path, "w") as f:
            f.write(content)
