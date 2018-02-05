import datetime
import io

from mir import sitemap


def test_write_sitemap_urlset_full():
    url1 = sitemap.URL(
        loc='http://localhost/',
        lastmod=datetime.date(2010, 1, 2),
        changefreq='daily',
        priority=0.5,
    )
    url2 = sitemap.URL('http://example.com/')
    file = io.StringIO()
    sitemap.write_sitemap_urlset(file, [url1, url2])
    assert file.getvalue() == """\
<?xml version='1.0' encoding='UTF-8'?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\
 xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\
 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\
<url><loc>http://localhost/</loc><lastmod>2010-01-02</lastmod><changefreq>daily</changefreq><priority>0.5</priority></url>\
<url><loc>http://example.com/</loc></url>\
</urlset>"""
