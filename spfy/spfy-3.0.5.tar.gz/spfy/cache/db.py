import os
import re
import time
import random
from io import BytesIO
from enum import IntEnum
from uuid import UUID, NAMESPACE_URL, uuid4, uuid5
from datetime import date, datetime

import aiohttp
import requests
import psycopg2.extras
from first import first
# pylint: disable=unused-import
from pony.orm import (
    Set,
    Json,
    Database,
    Optional,
    Required,
    PrimaryKey,
    ObjectNotFound,
    get,
    desc,
    select,
    ormtypes,
    sql_debug,
    db_session,
    composite_key
)
from pycountry import countries
from colorthief import ColorThief
from unsplash.errors import UnsplashError
from psycopg2.extensions import register_adapter

from .. import Unsplash, config, logger
from ..constants import TimeRange

register_adapter(ormtypes.TrackedDict, psycopg2.extras.Json)

if os.getenv('SQL_DEBUG'):
    sql_debug(True)
    import logging
    logging.getLogger('pony.orm.sql').setLevel(logging.DEBUG)

db = Database()


class ImageMixin:
    def image(self, width=None, height=None):
        if width:
            image = self.images.select().where(lambda i: i.width >= width).order_by(Image.width).first()
        elif height:
            image = self.images.select().where(lambda i: i.height >= height).order_by(Image.height).first()
        else:
            image = self.images.select().order_by(desc(Image.width)).first()

        return image

    def get_image_queries(self):
        words = self.name.split()
        stems = [[w[:i] for i in range(len(w), 2, -1)] for w in words]
        queries = [*words, self.name, *sum(stems, [])]
        return [f'{query} music' for query in queries]

    async def fetch_unsplash_image(self, width=None, height=None):
        image = self.image(width, height)
        if image:
            return image

        queries = self.get_image_queries()
        photo = None
        for query in queries:
            try:
                photos = await Unsplash.photo.random(query=query, orientation='squarish')
            except UnsplashError:
                continue

            if photos:
                photo = photos[0]
                break
        else:
            photo = (await Unsplash.photo.random(query='music', orientation='squarish'))[0]

        if photo is None:
            return None

        images = select(i for i in Image if i.url == photo.urls.full).for_update()
        if images.exists():
            for image in images:
                image.set(**{self.__class__.__name__.lower(): self})
            return self.image(width, height)

        ratio = photo.height / photo.width
        params = {
            self.__class__.__name__.lower(): self,
            'color': photo.color,
            'unsplash_user_fullname': photo.user.name,
            'unsplash_user_username': photo.user.username,
        }

        Image(url=photo.urls.full, width=photo.width, height=photo.height, **params)
        Image(url=photo.urls.regular, width=Image.REGULAR, height=int(round(ratio * Image.REGULAR)), **params)
        Image(url=photo.urls.small, width=Image.SMALL, height=int(round(ratio * Image.SMALL)), **params)
        Image(url=photo.urls.thumb, width=Image.THUMB, height=int(round(ratio * Image.THUMB)), **params)
        return self.image(width, height)


class User(db.Entity):
    _table_ = 'users'

    DEFAULT_EMAIL = 'spfy@backend'
    DEFAULT_USERNAME = 'spfy-backend'
    DEFAULT_USERID = uuid5(NAMESPACE_URL, DEFAULT_USERNAME)

    id = PrimaryKey(UUID, default=uuid4)  # pylint: disable=redefined-builtin
    email = Required(str, unique=True, index=True)
    username = Required(str, unique=True, index=True)
    country = Required('Country')
    display_name = Optional(str)
    birthdate = Optional(date)
    token = Required(Json, volatile=True)
    api_calls = Required(int, default=0, volatile=True)
    created_at = Required(datetime, default=datetime.now)
    last_usage_at = Required(datetime, default=datetime.now)

    top_artists = Set('Artist')
    disliked_artists = Set('Artist')

    top_genres = Set('Genre')
    disliked_genres = Set('Genre')

    top_countries = Set('Country')
    disliked_countries = Set('Country')

    top_cities = Set('City')
    disliked_cities = Set('City')

    top_expires_at = Optional(Json, volatile=True)

    def dislike(self, artist=None, genre=None, country=None, city=None):
        assert artist or genre or country or city
        if artist:
            self.disliked_artists.add(artist)
            self.top_artists.remove(artist)
        if genre:
            self.disliked_genres.add(genre)
            self.top_genres.remove(genre)
            self.disliked_artists.add(genre.artists)
            self.top_artists.remove(genre.artists)
        if country:
            self.disliked_countries.add(country)
            self.top_countries.remove(country)
        if city:
            self.disliked_cities.add(city)
            self.top_cities.remove(city)

    def top_expired(self, time_range):
        time_range = TimeRange(time_range).value
        return (
            not self.top_expires_at or time_range not in self.top_expires_at
            or time.time() >= self.top_expires_at[time_range]
        )

    @classmethod
    def default(cls):
        try:
            return User[cls.DEFAULT_USERID]
        except ObjectNotFound:
            return User(
                id=cls.DEFAULT_USERID,
                username=cls.DEFAULT_USERNAME,
                email=cls.DEFAULT_EMAIL,
                token={},
                country=Country.from_str(code='US')
            )

    @staticmethod
    def token_updater(_id):
        @db_session
        def update(token):
            User[_id].token = token

        return update


class Image(db.Entity):
    _table_ = 'images'

    REGULAR = 1080
    SMALL = 400
    THUMB = 200

    url = PrimaryKey(str)
    height = Optional(int)
    width = Optional(int)
    color = Optional(str)
    playlist = Optional('Playlist')
    artist = Optional('Artist')
    genre = Optional('Genre')
    country = Optional('Country')
    city = Optional('City')
    unsplash_user_fullname = Optional(str)
    unsplash_user_username = Optional(str)

    # pylint: disable=no-self-use
    def unsplash_url(self):
        return f'https://unsplash.com/?utm_source={config.unsplash.app_name}&utm_medium=referral'

    def unsplash_user_url(self):
        return f'https://unsplash.com/@{self.unsplash_user_username}?utm_source={config.unsplash.app_name}&utm_medium=referral'

    def unsplash_credits(self):
        return {
            'user_name': self.unsplash_user_fullname,
            'user_url': self.unsplash_user_url(),
            'site_url': self.unsplash_url()
        }

    @staticmethod
    async def grab_color_async(image_url):
        async with aiohttp.ClientSession() as client:
            async with client.get(image_url) as resp:
                image_file = BytesIO(await resp.read())
                color = ColorThief(image_file).get_color(quality=1)
                return f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'

    @staticmethod
    def grab_color(image_url):
        resp = requests.get(image_url)
        image_file = BytesIO(resp.content)
        color = ColorThief(image_file).get_color(quality=1)
        return f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'


class SpotifyUser(db.Entity):
    _table_ = 'spotify_users'

    id = PrimaryKey(str)  # pylint: disable=redefined-builtin
    name = Optional(str)
    playlists = Set('Playlist')

    @property
    def uri(self):
        return f'spotify:user:{self.id}'

    @property
    def href(self):
        return f'https://api.spotify.com/v1/users/{self.id}'

    @property
    def external_url(self):
        return f'http://open.spotify.com/user/{self.id}'


class Genre(db.Entity, ImageMixin):
    _table_ = 'genres'

    name = PrimaryKey(str)
    artists = Set('Artist')
    playlists = Set('Playlist')
    fans = Set(User, reverse='top_genres', table='genre_fans')
    haters = Set(User, reverse='disliked_genres', table='genre_haters')
    images = Set(Image, cascade_delete=True)

    def play(self, client, device=None):
        popularity = random.choice(list(Playlist.Popularity)[:3])
        playlist = client.genre_playlist(self.name, popularity)
        return playlist.play(device=device)


class Country(db.Entity, ImageMixin):
    _table_ = 'countries'

    name = PrimaryKey(str)
    code = Required(str, index=True, max_len=2)
    users = Set('User')
    cities = Set('City')
    playlists = Set('Playlist')
    fans = Set(User, reverse='top_countries', table='country_fans')
    haters = Set(User, reverse='disliked_countries', table='country_haters')
    images = Set(Image, cascade_delete=True)

    @staticmethod
    def _name_match(country, name):
        try:
            return name in country.name.lower() or name in country.official_name.lower()
        except:
            return False

    @classmethod
    def from_str(cls, name=None, code=None):

        iso_country = None
        if name == 'UK':
            iso_country = countries.get(alpha_2='GB')
        elif name == 'USA':
            iso_country = countries.get(alpha_2='US')
        elif name is not None:
            try:
                iso_country = countries.get(name=name)
            except KeyError:
                try:
                    iso_country = countries.get(official_name=name)
                except KeyError:
                    iso_country = first(countries, key=lambda c: cls._name_match(c, name.lower()))
        elif code is not None:
            try:
                iso_country = countries.get(alpha_2=code)
            except KeyError:
                iso_country = first(countries, key=lambda c: code.lower() in c.alpha_2.lower())

        if not iso_country:
            logger.error(f'Could not find a country with name={name} and code={code}')
            return None

        return cls.get(name=iso_country.name) or cls(name=iso_country.name, code=iso_country.alpha_2)

    def get_image_queries(self):
        words = self.name.split()
        stems = [[w[:i] for i in range(len(w), 2, -1)] for w in words]
        queries = [self.name, *words, *sum(stems, [])]
        return queries


class City(db.Entity, ImageMixin):
    _table_ = 'cities'

    name = PrimaryKey(str)
    country = Required(Country)
    playlists = Set('Playlist')
    fans = Set(User, reverse='top_cities', table='city_fans')
    haters = Set(User, reverse='disliked_cities', table='city_haters')
    images = Set(Image, cascade_delete=True)

    def get_image_queries(self):
        words = self.name.split()
        stems = [[w[:i] for i in range(len(w), 2, -1)] for w in words]
        queries = [self.name, self.country.name, *words, *sum(stems, [])]
        return queries


class Playlist(db.Entity, ImageMixin):
    _table_ = 'playlists'

    YEAR = '(?P<year>[0-9]{4})'
    GENRE = '(?P<genre>.+)'
    CITY = '(?P<city>.+)'
    COUNTRY = '(?P<country>.+)'
    COUNTRY_CODE = '(?P<country_code>[A-Z]{2})'
    DATE = '(?P<date>[0-9]{8})'
    GENRE_POPULARITY_TITLE = '(?P<popularity>Sound|Pulse|Edge)'
    GENRE_POPULARITY_LOWER = '(?P<popularity>sound|pulse|edge)'
    NEEDLE_POPULARITY = '(?P<popularity>Current|Emerging|Underground)'

    PATTERNS = {
        'sound_of_genre': re.compile(f'The {GENRE_POPULARITY_TITLE} of {GENRE}'),
        'sound_of_city': re.compile(f'The Sound of {CITY} {COUNTRY_CODE}'),
        'needle': re.compile(f'The Needle / {COUNTRY} {DATE}(?: - {NEEDLE_POPULARITY})?'),
        'pine_needle': re.compile(f'The Pine Needle / {COUNTRY}'),
        'year_in_genre': re.compile(f'{YEAR} in {GENRE}'),
        'meta_genre': re.compile(f'Meta{GENRE_POPULARITY_LOWER}: {GENRE}'),
        'meta_year_in_genre': re.compile(f'Meta{YEAR}: {GENRE}'),
    }

    class Popularity(IntEnum):
        SOUND = 0
        PULSE = 1
        EDGE = 2

        CURRENT = 3
        EMERGING = 4
        UNDERGROUND = 5

        YEAR = 6
        ALL = 7

    id = PrimaryKey(str)  # pylint: disable=redefined-builtin
    collaborative = Required(bool)
    name = Required(str)
    description = Optional(str)
    owner = Required(SpotifyUser)
    public = Required(bool)
    snapshot_id = Required(str)
    tracks = Required(int)
    popularity = Optional(int, index=True)
    genre = Optional(Genre)
    country = Optional(Country)
    city = Optional(City)
    date = Optional(date)
    christmas = Optional(bool, index=True)
    meta = Optional(bool, index=True)
    images = Set(Image, cascade_delete=True)
    composite_key(genre, popularity, meta)

    def play(self, client, device=None):
        return client.start_playback(playlist=self.uri, device=device)

    @property
    def uri(self):
        return f'spotify:user:{self.owner.id}:playlist:{self.id}'

    @property
    def href(self):
        return f'https://api.spotify.com/v1/users/{self.owner.id}/playlists/{self.id}'

    @property
    def external_url(self):
        return f'http://open.spotify.com/user/{self.owner.id}/playlist/{self.id}'

    @classmethod
    def get_fields(cls, groups):
        fields = {}
        if 'year' in groups:
            year = groups['year']

            fields['date'] = datetime(int(year), 1, 1)
            fields['popularity'] = cls.Popularity.YEAR.value

        if 'genre' in groups:
            genre = groups['genre'].lower()

            fields['genre'] = Genre.get(name=genre) or Genre(name=genre)
            fields['christmas'] = 'christmas' in genre

        if 'city' in groups and 'country_code' in groups:
            city = groups['city']
            country_code = groups['country_code']

            fields['country'] = Country.from_str(code=country_code)
            fields['city'] = City.get(name=city) or City(name=city, country=fields['country'])
            fields['popularity'] = cls.Popularity.SOUND.value

        if 'country' in groups:
            country = groups['country']

            fields['country'] = Country.from_str(name=country)

        if 'date' in groups:
            _date = groups['date']

            fields['date'] = datetime.strptime(_date, '%Y%m%d').date()

        if 'popularity' in groups:
            popularity = groups['popularity']
            if popularity:
                fields['popularity'] = cls.Popularity[popularity.upper()].value
            else:
                fields['popularity'] = cls.Popularity.ALL.value

        return fields

    @classmethod
    def from_dict(cls, playlist):  # pylint: disable=too-many-return-statements,too-many-statements
        owner = (
            SpotifyUser.get(id=playlist.owner.id)
            or SpotifyUser(id=playlist.owner.id, name=playlist.owner.get('display_name', playlist.owner.id))
        )
        fields = {
            'id': playlist.id,
            'collaborative': playlist.collaborative,
            'name': playlist.name,
            'owner': owner,
            'public': playlist.public,
            'snapshot_id': playlist.snapshot_id,
            'tracks': playlist.tracks.total,
            'christmas': 'Pine Needle' in playlist.name or 'christmas' in playlist.name.lower(),
            'meta': playlist.name.startswith('Meta'),
            'images': [Image.get(url=im.url) or Image(**im) for im in playlist.images]
        }

        for pattern in cls.PATTERNS.values():
            match = pattern.match(playlist.name)
            if match:
                groups = match.groupdict()
                fields.update(cls.get_fields(groups))
                break
        else:
            logger.warning(f'No pattern matches the playlist: {playlist.name}')

        return cls(**fields)


class Artist(db.Entity, ImageMixin):
    _table_ = 'artists'

    id = PrimaryKey(str)  # pylint: disable=redefined-builtin
    name = Required(str, index=True)
    followers = Required(int)
    genres = Set(Genre)
    fans = Set(User, reverse='top_artists', table='artist_fans')
    haters = Set(User, reverse='disliked_artists', table='artist_haters')
    popularity = Optional(int)
    images = Set(Image, cascade_delete=True)

    def play(self, client, device=None):
        return client.start_playback(artist=self.uri, device=device)

    @property
    def uri(self):
        return f'spotify:artist:{self.id}'

    @property
    def href(self):
        return f'https://api.spotify.com/v1/artists/{self.id}'

    @property
    def external_url(self):
        return f'http://open.spotify.com/artist/{self.id}'

    @classmethod
    async def from_dict_async(cls, artist):
        if artist.images:
            try:
                color = await Image.grab_color_async(artist.images[-1].url)
            except:
                color = '#000000'

            for image in artist.images:
                image.color = color

        return cls.from_dict(artist, grab_image_color=False)

    @classmethod
    def from_dict(cls, artist, grab_image_color=True):
        if artist.images and grab_image_color:
            try:
                color = Image.grab_color(artist.images[-1].url)
            except:
                color = '#000000'

            for image in artist.images:
                image.color = color

        genres = [Genre.get(name=genre) or Genre(name=genre) for genre in artist.genres]
        images = [Image.get(url=image.url) or Image(**image) for image in artist.images]
        return cls(
            id=artist.id,
            name=artist.name,
            followers=artist.followers.total,
            genres=genres,
            images=images,
            popularity=artist.popularity
        )


if config.database.filename:
    config.database.filename = os.path.expandvars(config.database.filename)

db.bind(**config.database)
db.generate_mapping(create_tables=True)
