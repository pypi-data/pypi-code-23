import argparse
import requests
from termcolor import cprint
from bs4 import BeautifulSoup
description='',

url = 'https://cn.bing.com/dict/search'

parser = argparse.ArgumentParser(prog='cld')

parser.add_argument(
    'word',
    type=str,
    help="search the meanings of the word"
)


def search(word):
    param = {'q': word}
    r = requests.get(url, param)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    poses = soup.select('div.qdef > ul > li > span.pos')
    defs = soup.select('div.qdef > ul > li > span.def')
    describes = {}
    for p, d in zip(poses, defs):
        describes[p.get_text()] = d.get_text()
    return describes


def display(word, defs):
    cprint('\n' + word, 'red')
    for key in defs:
        cprint(key, 'cyan')
        print(defs[key])


def main():
    args = parser.parse_args()
    word = args.word
    defs = search(word)
    display(word, defs)


if __name__ == '__main__':
    main()
