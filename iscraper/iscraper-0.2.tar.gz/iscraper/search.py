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
      print(prog_block.find('a')['title'])
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
      title = episode.find('div', {'class':'content-item__title'}).text.split(':')
      prog['episode_title'] = title[-1].strip()
      try:
        prog['episode'] = int(prog['episode_title'].split(' ')[-1])
      except ValueError:
        episode_title = prog['episode_title'].split('.', 1)
        prog['episode'] = int(episode_title[0])
        prog['episode_title'] = episode_title[1].strip()
      prog['series'] = int(title[0].split(' ')[-1])
      progs.append(prog)
    return sorted(progs, key=lambda p: '{:2}:{:2}'.format(p['series'],p['episode']))
