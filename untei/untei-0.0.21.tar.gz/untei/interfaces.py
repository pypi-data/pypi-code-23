def index_interface(config):
    def latest_articles(n):
        return __latest_articles__(config, None, n)

    def latest_articles_tagged_as(tag, n):
        return __latest_articles__(config, tag, n)


    variables = {
        "latest_articles"          : latest_articles,
        "latest_articles_tagged_as": latest_articles_tagged_as,
        "all_tags"                 : config.tags_to_article.keys(),
        "body"                     : ""
    }

    return variables

def tag_interface(config, tag):
    def latest_tagged_articles(n):
        return __latest_articles__(config, tag, n)
    variables = {
        "latest_tagged_articles": latest_tagged_articles,
        "tag"                   : tag,
        "tagged_articles"       : config.tags_to_article[tag],
        "body"                  : ""
    }

    return variables

def __latest_articles__(config, tag, n):
    if tag == None:
        return config.articles_ordered_by_date[:n]
    articles_list = []
    for a in config.articles_ordered_by_date:
        if tag in a.tags:
            articles_list.append(a)

    return articles_list[:n]
