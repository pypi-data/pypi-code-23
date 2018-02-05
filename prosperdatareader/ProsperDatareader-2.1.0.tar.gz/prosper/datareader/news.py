"""prosper.datareader.news: utilities for looking at news data"""

import pandas as pd

import prosper.datareader.robinhood as robinhood  # TODO: simplify import
import prosper.datareader.yahoo as yahoo
import prosper.datareader.intrinio as intrinio
import prosper.datareader.exceptions as exceptions
import prosper.datareader.config as config

def company_news_rh(
        ticker,
        page_limit=robinhood.news.PAGE_HARDBREAK,
        logger=config.LOGGER
):
    """get news items from Robinhood for a given company

    Args:
        ticker (str): stock ticker for desired company
        page_limit (int, optional): how many pages to allow in call
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): tabularized data for news

    """
    logger.info('Fetching company raw data feed for `%s` -- ROBINHOOD', ticker)
    raw_news_data = robinhood.news.fetch_company_news_rh(
        ticker.upper(),
        page_limit=page_limit,
        logger=logger
    )

    logger.info('--Pushing data into Pandas')
    news_df = pd.DataFrame(raw_news_data)
    news_df['published_at'] = pd.to_datetime(news_df['published_at'])

    logger.debug(news_df)
    return news_df

def company_news_intrinio(
        ticker,
        username='',
        password='',
        public_key='',
        endpoint_name='news',
        logger=config.LOGGER,
):
    """get news items from Intrinino

    Notes:
        credentials required from: https://intrinio.com/account
        username/password OR public_key, not both

    Args:
        ticker (str): stock ticker for desired company
        username (str): intrinio username
        password (str): intrinio password
        public_key (str): intrinio public_key
        logger (:obj:`logging.logger`): logging handle

    Returns:
        pandas.DataFrame: tabularized data for news

    Raises:
        exceptions.InvalidAuth: invalid auth pattern
        requests.exceptions: HTTP/connection errors

    """
    logger.info('Fetching company raw data feed for `%s` -- INTRININO', ticker)
    connection = intrinio.auth.IntrinioHelper(
        username=username,
        password=password,
        public_key=public_key,
    )
    raw_data = connection.request(
        endpoint_name,
        params={'ticker': ticker.upper()}
    )

    logger.info('--pushing data into Pandas')
    news_df = pd.DataFrame(raw_data['data'])
    news_df['publication_date'] = pd.to_datetime(news_df['publication_date'])

    logger.debug(news_df)
    return news_df

def company_headlines_yahoo(
        ticker,
        logger=config.LOGGER,
):
    """get news items from Yahoo for a given company

    Notes:
        Wraps https://developer.yahoo.com/finance/company.html

    Args:
        ticker (str): stock ticker for desired company
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): tabularized data for news

    Raises:
        requests.exceptions: HTTP/connection errors

    """
    logger.info('Fetching company raw data feed for `%s` -- yahoo', ticker)
    raw_data = yahoo.news.fetch_finance_headlines_yahoo(ticker)

    logger.info('--pushing data into Pandas')

    news_df = pd.DataFrame(raw_data)
    news_df['published'] = pd.to_datetime(news_df['published'])

    return news_df

def industry_headlines_yahoo(
        ticker,
        logger=config.LOGGER,
):
    """get news items from Yahoo for an industry segment given a ticker

    Notes:
        Wraps https://developer.yahoo.com/finance/industry.html

    Args:
        ticker (str): stock ticker for desired company
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): tabularized data for news

    Raises:
        requests.exceptions: HTTP/connection errors

    """
    logger.info('Fetching industry raw data feed for `%s` -- yahoo', ticker)
    raw_data = yahoo.news.fetch_finance_headlines_yahoo(
        ticker,
        uri=yahoo.news.INDUSTRY_NEWS_URL,
    )

    logger.info('--pushing data into Pandas')

    news_df = pd.DataFrame(raw_data)
    news_df['published'] = pd.to_datetime(news_df['published'])

    return news_df
