# coding: utf-8
from __future__ import absolute_import, unicode_literals

from operator import itemgetter

import pytest

from aioimdb import Imdb


@pytest.fixture(scope='function')
async def client():
    async with Imdb(locale='en_US') as client:
        yield client
    client.clear_cached_credentials()


@pytest.mark.asyncio
async def test_get_title_plot_synopsis(client):
    expected_keys = [
        '@type', 'id', 'plotSynopses', 'title', 'titleType', 'year'
    ]

    resource = await client.get_title_plot_synopsis('tt0111161')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_plot(client):
    expected_keys = ['@type', 'outline', 'summaries', 'totalSummaries']

    resource = await client.get_title_plot('tt0111161')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_user_reviews(client):
    expected_keys = [
        '@type', 'base', 'paginationKey', 'reviews', 'totalReviews'
    ]

    resource = await client.get_title_user_reviews('tt0111161')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_metacritic_reviews(client):
    expected_keys = [
        '@type', 'id', 'metaScore', 'metacriticUrl', 'reviewCount',
        'userRatingCount', 'userScore', 'reviews', 'title'
    ]

    resource = await client.get_title_metacritic_reviews('tt0111161')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_title_reviews_non_existant_title(client):
    with pytest.raises(LookupError):
        await client.get_title_user_reviews('tt9999999')


@pytest.mark.asyncio
async def test_title_exists(client):
    result = await client.title_exists('tt2322441')
    assert True is result


@pytest.mark.asyncio
async def test_title_exists_non_existant_title(client):
    result = await client.title_exists('tt0000000')
    assert False is result


@pytest.mark.asyncio
async def test_search_for_title_searching_title(client):
    results = await client.search_for_title('Shawshank redemption')
    expected_top_results = [
        {
            'imdb_id': 'tt0111161',
            'title': 'The Shawshank Redemption',
            'year': '1994',
            'type': 'feature',
        },
        {
            'imdb_id': 'tt5443386',
            'title': 'The Shawshank Redemption: Behind the Scenes',
            'year': '2004',
            'type': 'video',
        },
    ]
    assert len(results) > 0
    assert expected_top_results == results[:2]


@pytest.mark.asyncio
@pytest.mark.parametrize('query', [
    'Mission: Impossible',
    'Honey, I Shrunk the Kids',
    '4.3.2.1. (2010)',
    '500 Days of Summer (2009)',
    '$9.99 (2008)',
    'Goonies 1986',
    '[REC] (2007)',
    '[REC]² (2009)',
    '[REC]³ Genesis (2012)',
    '¡Three Amigos! (1986)',
    '(Untitled) (2009)',
])
async def test_search_for_title_input_with_special_chars(query, client):
    results = await client.search_for_title(query)
    assert len(results) > 0


@pytest.mark.asyncio
async def test_search_for_name(client):
    results = await client.search_for_name('Andrew Lloyd Webber')

    assert len(results) > 0
    expected_results = [
        {'name': 'Andrew Lloyd Webber', 'imdb_id': 'nm0515908'},
    ]
    assert (sorted(expected_results, key=itemgetter('imdb_id')) ==
            sorted(results, key=itemgetter('imdb_id')))


@pytest.mark.asyncio
async def test_search_for_title_no_results(client):
    results = await client.search_for_title('898582da396c93d5589e0')
    assert [] == results


@pytest.mark.asyncio
async def test_get_popular_titles(client):
    expected_keys = ['@type', 'id', 'ranks']

    resource = await client.get_popular_titles()

    assert sorted(resource.keys()) == sorted(expected_keys)
    assert len(resource['ranks']) == 100


@pytest.mark.asyncio
async def test_get_popular_shows(client):
    expected_keys = ['@type', 'id', 'ranks']

    resource = await client.get_popular_shows()

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_popular_movies(client):
    expected_keys = ['@type', 'id', 'ranks']

    resource = await client.get_popular_shows()

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_name(client):
    expected_keys = [
        '@type', 'base', 'id', 'jobs', 'knownFor', 'quotes',
        'trivia'
    ]

    resource = await client.get_name('nm0000151')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_name_filmography(client):
    expected_keys = ['@type', 'filmography']

    resource = await client.get_name_filmography('nm0000151')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title(client):
    imdb_id = 'tt0111161'
    expected_keys = [
        '@type', 'base', 'filmingLocations', 'metacriticScore', 'plot',
        'ratings', 'similarities', 'soundtrack'
    ]

    resource = await client.get_title(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_genres(client):
    imdb_id = 'tt0111161'
    expected_keys = ['@type', 'genres', 'id', 'title', 'titleType', 'year']

    resource = await client.get_title_genres(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_similarities(client):
    imdb_id = 'tt0111161'
    expected_keys = ['@type', 'base', 'id', 'similarities']

    resource = await client.get_title_similarities(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_awards(client):
    imdb_id = 'tt0111161'
    expected_keys = ['@type', 'awards', 'id']

    resource = await client.get_title_awards(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_releases(client):
    imdb_id = 'tt0111161'
    expected_keys = ['@type', 'releases', 'id', 'title', 'titleType', 'year']

    resource = await client.get_title_releases(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_versions(client):
    imdb_id = 'tt0111161'
    expected_keys = [
        '@type', 'alternateTitles', 'alternateVersions', 'colorations',
        'defaultTitle', 'silent', 'spokenLanguages', 'originalTitle',
        'origins', 'runningTimes', 'id', 'title', 'titleType', 'year'
    ]

    resource = await client.get_title_versions(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_ratings(client):
    imdb_id = 'tt0111161'
    expected_keys = [
        '@type', 'id', 'title', 'titleType', 'year', 'bottomRank',
        'canRate', 'rating', 'ratingCount', 'topRank'
    ]

    resource = await client.get_title_ratings(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_quotes(client):
    imdb_id = 'tt0111161'
    expected_keys = ['@type', 'quotes', 'id', 'title', 'titleType', 'year']

    resource = await client.get_title_quotes(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_connections(client):
    imdb_id = 'tt0111161'
    expected_keys = ['@type', 'base', 'connections']

    resource = await client.get_title_connections(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_credits(client):
    imdb_id = 'tt0111161'
    expected_keys = ['@type', 'base', 'creditsSummary', 'id', 'credits']

    resource = await client.get_title_credits(imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_credits_with_redirection_result(client):
    redir_imdb_id = 'tt0000021'

    with pytest.raises(LookupError):
        await client.get_title_credits(redir_imdb_id)


@pytest.mark.asyncio
async def test_get_title_redirection_result(client):
    redir_imdb_id = 'tt0000021'

    with pytest.raises(LookupError):
        await client.get_title(redir_imdb_id)


@pytest.mark.asyncio
async def test_get_title_excludes_episodes(client):
    episode_imdb_id = 'tt3181538'
    assert await client.get_title(episode_imdb_id) is not None

    with pytest.raises(LookupError) as exc:
        async with Imdb(exclude_episodes=True) as imdb:
            await imdb.get_title(episode_imdb_id)

    exc.match(r'Title not found. Title was an episode.+')


@pytest.mark.asyncio
async def test_get_title_episodes(client):
    tv_show_imdb_id = 'tt0303461'
    expected_keys = ['@type', 'base', 'id', 'seasons']

    resource = await client.get_title_episodes(tv_show_imdb_id)

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_episodes_raises_when_exclude_episodes_enabled():
    async with Imdb(exclude_episodes=True) as client:
        with pytest.raises(ValueError):
            await client.get_title_episodes('tt0303461')


@pytest.mark.asyncio
async def test_get_title_episodes_raises_imdb_id_is_not_that_of_a_tv_show(
        client):
    non_show_imdb_id = 'tt0468569'
    with pytest.raises(LookupError):
        await client.get_title_episodes(non_show_imdb_id)


@pytest.mark.asyncio
async def test_get_name_images(client):
    expected_keys = ['@type', 'images', 'totalImageCount']

    resource = await client.get_name_images('nm0000032')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_name_videos(client):
    expected_keys = [
        '@type', 'akas', 'id', 'image', 'legacyNameText', 'name', 'size',
        'videoCounts', 'videos'
    ]

    resource = await client.get_name_videos('nm0000032')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_images(client):
    expected_keys = ['@type', 'images', 'totalImageCount']

    resource = await client.get_title_images('tt0111161')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_videos(client):
    expected_keys = [
        '@type', 'id', 'image', 'size', 'title', 'titleType', 'videoCounts',
        'videos', 'year'
    ]

    resource = await client.get_title_videos('tt0111161')

    assert sorted(resource.keys()) == sorted(expected_keys)


@pytest.mark.asyncio
async def test_get_title_raises_not_found(client):
    with pytest.raises(LookupError):
        await client.get_title('tt9999999')


@pytest.mark.asyncio
@pytest.mark.parametrize('imdb_id, exp_valid', [
    ('tt1234567', True),
    ('nm1234567', True),
    ('x', False),
    (1234567, False),
    (None, False),
])
async def test_validate_imdb_id(imdb_id, exp_valid, client):

    if exp_valid:
        # no raise
        client.validate_imdb_id(imdb_id)
    else:
        with pytest.raises(ValueError):
            client.validate_imdb_id(imdb_id)
