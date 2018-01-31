import requests
import random
from bs4 import BeautifulSoup
import urllib

def __get_gr_page(page):
  url = 'https://www.goodreads.com/quotes?page={}'.format(page)
  return  requests.get(url)

def __select_random_element(short_quotes):
    quote_number = random.randint(0,len(short_quotes) - 1)
    return short_quotes[quote_number]

def generate_quote():
  try:
    page_number = random.randint(1,100)
    response = __get_gr_page(page_number)

    soup = BeautifulSoup(response.content, 'html.parser')
    quotes = soup.find_all('div', class_='quoteText', limit=5)
    short_quotes = [quote.text for quote in quotes if len(quote.text) < 400]

    return __select_random_element(short_quotes)
  except Exception as ex:
    print('Failed request to page: {} with error: {}'.format(page_number, ex))


if __name__ == '__main__':
  print('\nPreparing your quote of the day 🤓...')
  selected_quote = generate_quote()
  print(selected_quote)