import json
import re
import sys

import bs4
import requests


def search_movies(search_term):
    response = requests.get('http://www.boxofficemojo.com/search/', params={
        'q': search_term
    })
    response.raise_for_status()

    document = bs4.BeautifulSoup(response.content, 'html.parser')

    movie_link_pattern = re.compile(r'/movies/\?id=([\w\-\.]+)')

    def movie_from_row(row):
        first_cell = row.select_one('td:nth-of-type(1)')
        if first_cell is None:
            return None, None

        movie_link = first_cell.find('a')
        if movie_link is None:
            return None, None

        movie_link_match = movie_link_pattern.search(movie_link['href'])
        if movie_link_match is None:
            return None, None

        return movie_link_match.group(1), first_cell.text.strip()

    results = []
    for row in document.find_all('tr'):
        movie_id, title = movie_from_row(row)
        if movie_id:
            # If there's a highlighted row, that's an exact match.
            results.append({
                'movie_id': movie_id,
                'title': title,
                'exact': row['bgcolor'] == '#FFFF99'
            })

    return results


def get_movie_id(search_term):
    results = search_movies(search_term)

    exact_match = next((result for result in results if result['exact']), None)
    if exact_match is not None:
        return exact_match['movie_id']

    # Otherwise, if there's exactly one match, return that.
    if len(results) == 1:
        return results[0]['movie_id']

    # In any other case, return None since there isn't an unambiguous result.
    return None


def get_box_office(movie_id):
    response = requests.get('http://www.boxofficemojo.com/movies/', params={
        'id': movie_id,
        'page': 'daily',
        'view': 'chart'
    })
    response.raise_for_status()

    document = bs4.BeautifulSoup(response.content, 'html.parser')
    title_match = re.search(r'(.*) - Daily Box Office Results',
                            document.title.text)
    if title_match is None:
        raise MovieNotFound(movie_id)

    result = {
        'title': title_match.group(1),
        'href': response.url,
        'box_office': []
    }

    chart = document.find(id='chart_container')

    if chart is None:
        return result

    table = chart.next_sibling
    rows = table.find_all('tr')

    box_office = result['box_office']
    gross_pattern = re.compile(r'\$\d[\d,]+')

    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 10:
            continue

        day, date, rank, gross, _, _, theaters, _, cumulative = [
            cell.text for cell in cells[:9]]
        if not gross_pattern.match(gross):
            continue

        box_office.append({
            'day': day,
            'date': date,
            'rank': parse_int(rank),
            'gross': parse_int(gross),
            'theaters': parse_int(theaters),
            'cumulative': parse_int(cumulative)
        })

    return result


class MovieNotFound(Exception):
    def __init__(self, movie_id):
        self.movie_id = movie_id

    def __str__(self):
        return '"%s" not found' % self.movie_id


def parse_int(value):
    try:
        return int(re.sub(r'[$,]', '', value))
    except ValueError:
        return None


if __name__ == '__main__':
    search_term = sys.argv.pop()
    movie_id = get_movie_id(search_term)
    box_office = get_box_office(movie_id)
    json.dump(box_office, sys.stdout)
