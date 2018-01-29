import components

body = ""
for article in latest_tagged_articles(10):
    body = body + components.create_short_article_box(article) + "<br />"
