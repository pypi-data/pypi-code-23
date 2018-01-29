import components

body = ""
for a in latest_articles(10):
    body = body + components.create_short_article_box(a) + "<br />"
