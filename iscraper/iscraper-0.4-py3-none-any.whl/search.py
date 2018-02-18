import urllib.request
from bs4 import BeautifulSoup

def search_url(title):
  return 'https://www.bbc.co.uk/iplayer/search?{}'.format(
      urllib.parse.urlencode({'q':title}))

def programme_id(title):
  urls = []
  with urllib.request.urlopen(search_url(title)) as search_page:
    search_soup = BeautifulSoup(search_page.read(), 'html.parser')
    prog_block = search_soup.find('li', {'class':'programme'})
    if prog_block and \
        prog_block.find('a')['title'].split(',',1)[0].upper() == title.upper():
      return prog_block['data-ip-id']
    else:
      return None

def episodes(prog_id):
  progs = []
  with urllib.request.urlopen(
      'https://www.bbc.co.uk/iplayer/episodes/{}'.
        format(prog_id)) as episodes_page:
    episodes_soup = BeautifulSoup(episodes_page.read(), 'html.parser')
    brand = episodes_soup.find('h1', {'class':'hero-header__title'}).text
    for episode in episodes_soup('a',{'class':'content-item__link'}):
      prog = { 
        'brand': brand,
        'pid': episode['href'].split('/')[3],
      }
      prog.update(programme_from_title(episode.find('div', 
          {'class':'content-item__title'}).text))
      progs.append(prog)
    return sorted(progs, key=lambda p: '{:2}:{:2}'.format(p['series'],p['episode']))

def programme_from_title(title):
  try:
    #Series 1: Episode 2
    [series, episode] = title.strip().split(':', 1)
    [series_name, series_number] = series.split(' ', 1)
    series_number = int(series_number)
    episode_title = episode.strip()
  except ValueError:
    #3. Episode Title
    series_number = 1
    episode_title = title
  [_, episode_number] = episode_title.split(' ', 1)
  try:
    episode_number = int(episode_number)
  except ValueError:
    #Series 1: 2. Episode Title
    [episode_number, episode_title] = episode_title.split('.', 1)
    episode_number = int(episode_number)
    episode_title = episode_title.strip()
    
  return {
    'series': series_number,
    'episode': episode_number,
    'episode_title': episode_title,
  }

def films_from_page(page=1):
  with urllib.request.urlopen(
      'https://www.bbc.co.uk/iplayer/categories/films/all?{}'.format(
        urllib.parse.urlencode({'sort':'atoz','page':page}))) as films_page:
    page_soup = BeautifulSoup(films_page, 'html.parser')
    films = [{'pid': f['data-ip-id'], 'title': f.find('a')['title']} 
             for f in page_soup('li', {'class': 'programme'})]
    if films:
      return films + films_from_page(page + 1)
    else:
      return []

def films():
  return films_from_page()
