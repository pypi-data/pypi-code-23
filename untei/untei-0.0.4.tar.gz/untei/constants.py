import sys

def _path_concatinate(p1, p2):
    if p1[len(p1)-1] == "/" and p2[0] == "/":
        return p1 + p2[1:]
    elif p1[len(p1)-1] == "/" and p2[0] != "/":
        return p1 + p2
    elif p1[len(p1)-1] != "/" and p2[0] == "/":
        return p1 + p2
    else:
        return p1 + "/" + p2

class Const:
    # arguments
    FILES_PATH = sys.argv[1] + "/"
    # Essential file names
    OUTPUT_DIRECTORY =  _path_concatinate(FILES_PATH, "output/")
    SITE_CONFIG_PATH  = _path_concatinate(FILES_PATH, "theme/site_config.txt")
    SITE_CONFIG_KEY_TITLE = "title"
    SITE_CONFIG_KEY_COPYRIGHT = "copyright"
    SITE_CONFIG_KEYS = { SITE_CONFIG_KEY_TITLE, SITE_CONFIG_KEY_COPYRIGHT }
    SITE_CONFIG_TAG = _path_concatinate(FILES_PATH, "theme/tag.py")
    SITE_CONFIG_INDEX = _path_concatinate(FILES_PATH, "theme/index.py")
    SITE_CONFIG_AUTHOR = "/theme/author.py"

    # Article attributes
    ## Status
    ARTICLE_STATUS = "ArticleStatus"
    ARTICLE_STATUS_READY = "ArticleStatusReady"
    ARTICLE_STATUS_DRAFT = "ArticleStatusDraft"

    ## Title
    ARTICLE_TITLE = "ArticleTitle"

    ## Tags
    ARTICLE_TAG = "ArticleTag"
    ARTICLE_TAGS = "ArticleTags"

    ## Authors
    ARTICLE_AUTHOR = "ArticleAuthor"
    ARTICLE_AUTHORS = "ArticleAuthors"

    ## Template
    TEMPLATE_ARTICLE = FILES_PATH + "theme/template.html"
    TEMPLATE_SITE_TITLE_INDICATOR = "{{site_config.title}}"
    TEMPLATE_COPYRIGHT_INDICATOR = "{{site_config.copyright}}"
    TEMPLATE_CONTENT_INDICATOR = "{{article.content}}"
    TEMPLATE_ARTICLE_TITLE = "{{article.title}}"
    TEMPLATE_VARIABLES = [ TEMPLATE_SITE_TITLE_INDICATOR, TEMPLATE_CONTENT_INDICATOR, TEMPLATE_COPYRIGHT_INDICATOR ]

    # File type
    FILE_TYPE = "FileType"
    FILE_TYPE_MARKDOWN = "FileTypeMarkdown"
    FILE_TYPE_DIRECTORY = "FileTypeDirectory"
    EXTENSIONS_FOR_MARKDOWN = [ ".md", ".markdown", ".mdown" ]
    FILE_TYPE_HTML = "FileTypeHtml"
    EXTENSIONS_FOR_HTML = [ ".html", ".htm" ]




    # other keywords
    FILE_PATH = "FilePath"
