BASE_PATH = 'https://hacker-news.firebaseio.com/v0'

# noinspection SpellCheckingInspection
API_PATH = {
    'ask': 'askstories.json',
    'best': 'beststories.json',
    'item': 'item/{id}.json',
    'job': 'jobstories.json',
    'maxitem': 'maxitem.json',
    'new': 'newstories.json',
    'show': 'showstories.json',
    'top': 'topstories.json',
    'updates': 'updates.json',
    'user': 'user/{user}.json',
}

ITEM_BASE_URL = 'https://news.ycombinator.com/item?id={id}'
USER_BASE_URL = 'https://news.ycombinator.com/user?id={user}'
DEFAULT_LIMIT = 25
