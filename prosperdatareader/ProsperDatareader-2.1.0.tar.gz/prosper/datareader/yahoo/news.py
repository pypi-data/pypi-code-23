"""prosper.datareader.yahoo.news: parse news feeds from yahoo"""
from six.moves.html_parser import HTMLParser
import requests
import feedparser
import pandas as pd

DROP_COLUMNS = [
    'guidislink', 'links', 'summary_detail', 'title_detail', 'published_parsed', # Company list
    'media_credit', 'media_content', 'media_text', 'source',                     # Industry list
]
COMPANY_NEWS_URL = 'http://finance.yahoo.com/rss/headline'
INDUSTRY_NEWS_URL = 'http://finance.yahoo.com/rss/industry'
def fetch_finance_headlines_yahoo(
        ticker,
        drop_columns=DROP_COLUMNS,
        uri=COMPANY_NEWS_URL,
):
    """fetch & parse RSS feed from yahoo

    Args:
        ticker (str): company ticker to fetch
        drop_columns (:obj:`list`): list of columns not to report
        uri (str): headline endpoint

    Returns:
        dict: parsed RSS->JSON

    Raises:
        requests.exceptions: connection/HTTP errors

    """
    req = requests.get(
        url=uri,
        params={'s':ticker}
    )
    req.raise_for_status()

    raw_response = req.content.decode('utf-8')
    feed_df = pd.DataFrame(feedparser.parse(raw_response)['entries'])\
        .drop(drop_columns, axis=1, errors='ignore')

    feed_df['title'] = feed_df['title'].map(HTMLParser().unescape)
    feed_df['summary'] = feed_df['summary'].map(HTMLParser().unescape)
    # TODO: parse/encode utf-8

    return feed_df.to_dict(orient='records')
