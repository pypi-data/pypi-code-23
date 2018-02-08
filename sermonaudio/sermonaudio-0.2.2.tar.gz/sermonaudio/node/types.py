"""Node API data structures"""
import datetime
import dateutil.parser
import pytz

from enum import Enum


def isinstance_or_none(obj, type):
    return obj is None or isinstance(obj, type)


class Node:
    """The base node object, which encapsulates all node API responses"""
    def __init__(self, obj: dict):
        self.node_type = obj['nodeType']
        assert isinstance(self.node_type, str)

        self.node_display_name = obj['nodeDisplayName']
        assert isinstance(self.node_display_name, str)

        self.results = obj['results']
        assert (isinstance(self.results, list) or
                isinstance(self.results, dict) or
                self.results is None)

        self.total_count = obj['totalCount']
        assert isinstance_or_none(self.total_count, int)


class Source:
    """Broadcaster API data model"""
    def __init__(self, obj: dict):
        """Constructs a broadcaster from a dictionary returned from the SermonAudio API"""
        self.source_id = obj['sourceID']
        assert isinstance(self.source_id, str)

        self.service_times_are_preformatted = obj['serviceTimesArePreformatted']
        assert isinstance_or_none(self.service_times_are_preformatted, bool)

        self.service_times = obj['serviceTimes']
        assert isinstance_or_none(self.service_times, str)

        self.denomination = obj['denomination']
        assert isinstance_or_none(self.denomination, str)

        self.address = obj['address']
        assert isinstance_or_none(self.address, str)

        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.location = obj['location']
        assert isinstance(self.location, str)

        self.latitude = obj['latitude']
        assert isinstance_or_none(self.latitude, float)

        self.longitude = obj['longitude']
        assert isinstance_or_none(self.longitude, float)

        self.image_url = obj['imageURL']
        assert isinstance(self.image_url, str)

        self.album_art_url_format = obj['albumArtURL']
        assert isinstance(self.album_art_url_format, str)

        self.minister = obj['minister']
        assert isinstance_or_none(self.minister, str)

        self.phone = obj['phone']
        assert isinstance_or_none(self.phone, str)

        self.home_page_url = obj['homePageURL']
        assert isinstance_or_none(self.home_page_url, str)

        self.bible_version = obj['bibleVersion']
        assert isinstance_or_none(self.bible_version, str)

        self.facebook_username = obj['facebookUsername']
        assert isinstance_or_none(self.facebook_username, str)

        self.twitter_username = obj['twitterUsername']
        assert isinstance_or_none(self.twitter_username, str)

        self.about_us = obj['aboutUs']
        assert isinstance_or_none(self.about_us, str)

        self.webcast_in_progress = obj['webcastInProgress']
        assert isinstance(self.webcast_in_progress, bool)

        self.vacant_pulpit = obj['vacantPulpit']
        assert isinstance(self.vacant_pulpit, bool)

        self.disabled = obj['disabled']
        assert isinstance(self.disabled, bool)

    def get_album_art_url(self, size: int):
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace('{size}', str(size))


class Speaker:
    """Speaker data model"""
    def __init__(self, obj: dict):
        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.sort_name = obj.get('sortName')
        assert isinstance(self.sort_name, str)

        self.bio = obj['bio']
        assert isinstance_or_none(self.bio, str)

        self.portrait_url = obj['portraitURL']
        assert isinstance(self.portrait_url, str)

        self.rounded_thumbnail_image_url = obj['roundedThumbnailImageURL']
        assert isinstance(self.rounded_thumbnail_image_url, str)

        self.album_art_url_format = obj['albumArtURL']
        assert isinstance(self.album_art_url_format, str)

    def get_album_art_url(self, size: int):
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace('{size}', str(size))


class Sermon:
    """Sermon data model"""
    def __init__(self, obj: dict):
        """Constructs a sermon from a dictionary returned from the SermonAudio API"""
        self.sermon_id = obj['sermonID']
        assert isinstance(self.sermon_id, str)

        self.source = Source(obj['source'])
        self.speaker = Speaker(obj['speaker'])

        self.audio_duration_in_seconds = obj['audioDurationInSeconds']
        assert isinstance_or_none(self.audio_duration_in_seconds, int)

        self.video_duration_in_seconds = obj['videoDurationInSeconds']
        assert isinstance_or_none(self.video_duration_in_seconds, int)

        self.full_title = obj['fullTitle']
        assert isinstance(self.full_title, str)

        self.display_title = obj['displayTitle']
        assert isinstance(self.display_title, str)

        self.subtitle = obj['subtitle']
        assert isinstance_or_none(self.subtitle, str)

        self.preach_date = datetime.datetime.strptime(obj['preachDate'], '%Y-%m-%d').date()
        assert isinstance(self.preach_date, datetime.date)

        self.language_code = obj['languageCode']
        assert isinstance(self.language_code, str)

        self.bible_text = obj['bibleText']
        assert isinstance_or_none(self.bible_text, str)

        self.more_info_text = obj['moreInfoText']
        assert isinstance_or_none(self.more_info_text, str)

        self.event_type = obj['eventType']
        assert isinstance(self.event_type, str)

        self.download_count = obj['downloadCount']
        assert isinstance(self.download_count, int)

        self.audio_bitrate = obj['audioBitrate']
        assert isinstance_or_none(self.audio_bitrate, int)

        self.video_bitrate = obj['videoBitrate']
        assert isinstance_or_none(self.video_bitrate, int)

        self.audio_file_url = obj['audioFileURL']
        assert isinstance_or_none(self.audio_file_url, str)

        self.audio_file_lo_url = obj['audioFileLOURL']
        assert isinstance_or_none(self.audio_file_lo_url, str)

        self.video_file_url = obj['videoFileURL']
        assert isinstance_or_none(self.video_file_url, str)

        self.video_file_lo_url = obj['videoFileLOURL']
        assert isinstance_or_none(self.video_file_lo_url, str)

        self.video_hls_url = obj['videoHLSURL']
        assert isinstance_or_none(self.video_hls_url, str)

        self.video_thumbnail_image_url = obj['videoThumbnailImageURL']
        assert isinstance_or_none(self.video_thumbnail_image_url, str)

        self.text_file_url = obj['textFileURL']
        assert isinstance_or_none(self.text_file_url, str)

    def __str__(self):
        return f'{self.speaker.display_name} - {self.display_title}'


class HLSStreamInfo:
    """An HLS video stream info object"""

    def __init__(self, bitrate: int, url: str):
        """Constructs an HLS stream info object"""
        self.bitrate = bitrate
        assert isinstance(self.bitrate, int)

        self.url = url
        assert isinstance(self.url, str)


class WebcastInfo:
    """Webcast info data model"""

    def __init__(self, obj: dict):
        """Constructs webcast info from a dictionary returned from the SermonAudio API"""
        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.source_id = obj['sourceID']
        assert isinstance(self.source_id, str)

        self.source_location = obj['sourceLocation']
        assert isinstance(self.source_location, str)

        self.start_time = datetime.datetime.fromtimestamp(obj['startTime'], tz=pytz.utc)
        assert isinstance(self.start_time, datetime.datetime)

        self.preview_image_url = obj['previewImageURL']
        assert isinstance_or_none(self.preview_image_url, str)

        self.resizable_preview_image_url = obj['resizablePreviewImageURL']
        assert isinstance_or_none(self.resizable_preview_image_url, str)

        self.peak_listener_count = obj['peakListenerCount']
        assert isinstance(self.peak_listener_count, int)

        self.total_tune_in_count = obj['totalTuneInCount']
        assert isinstance(self.total_tune_in_count, int)

        self.has_video = obj['hasVideo']
        assert isinstance(self.has_video, bool)

        self.audio_url = obj['audioURL']
        assert isinstance(self.audio_url, str)

        self.hls_video_streams = []
        for stream in obj['hlsVideoStreams']:
            stream_info = HLSStreamInfo(stream['bitrate'], stream['url'])
            self.hls_video_streams.append(stream_info)


class SourceNearLocation:
    """Model representing a source and it's distance from a search origin"""

    def __init__(self, obj: dict):
        """Constructs source near location from a dictionary returned from the SermonAudio API"""
        self.source = Source(obj['source'])
        assert isinstance(self.source, Source)

        self.meters = obj['meters']
        assert isinstance(self.meters, int)

    def __str__(self):
        return f'{self.source.source_id} - about {round(self.meters/1000, 1)}km away'


class GalleryItem:
    """One item in a gallery category, representing an image."""
    def __init__(self, obj: dict):
        self.type = obj.get('type')
        self.image = obj['image']
        self.category = obj['category']
        self.width = obj['width']
        self.height = obj['height']
        self.caption = obj['caption']
        self.display_caption = obj['displayCaption']
        self.url = obj['url']
        self.url_thumbnail = obj['urlThumbnail']


class EventItem:
    """An event item"""
    def __init__(self, obj: dict):
        self.type = obj.get('type')
        self.event_id = obj['eventID']
        self.title = obj['title']
        self.subtitle = obj['subtitle']
        self.category = obj['category']
        self.date_begin = dateutil.parser.parse(obj['dateBegin']).date() if obj['dateBegin'] is not None else None
        self.date_end = dateutil.parser.parse(obj['dateEnd']).date() if obj['dateEnd'] is not None else None
        self.time = obj['time']
        self.who = obj['who']
        self.cost = obj['cost']
        self.currency_type = obj['currencyType']
        self.url = obj['url']
        self.location_url = obj['locationUrl']
        self.video_url = obj['videoUrl']
        self.location_info = obj['locationInfo']
        self.location_geo_info_object = obj['locationGeoInfoObject']
        self.description = obj['description']
        self.notes = obj['notes']
        self.max_seats = obj['maxSeats']
        self.location_geo_info = obj['locationGeoInfo']
        self.accept_registration = obj['acceptRegistration']
        self.ec_flags = obj['ecFlags']

        # contained objects
        self.source = Source(obj['source'])
        self.background_image = GalleryItem(obj['backgroundImage']) if obj['backgroundImage'] is not None else None
        self.gallery = [GalleryItem(g) for g in obj['gallery'] if g is not None]
        self.speakers = [EventSpeaker(s) for s in obj['speakers']]
        self.schedule = [EventSchedule(s) for s in obj['schedule']]

        assert isinstance_or_none(self.background_image, GalleryItem)

        if self.gallery:
            for g in self.gallery:
                assert isinstance_or_none(g, GalleryItem)

        if self.speakers:
            for s in self.speakers:
                assert isinstance_or_none(s, EventSpeaker)

        if self.schedule:
            for s in self.schedule:
                assert isinstance_or_none(s, EventSchedule)


class EventSpeaker:
    """An event speaker"""
    def __init__(self, obj: dict):
        self.type = obj.get('type')
        self.sa_speaker_info = obj['saSpeakerInfo']
        self.speaker_rank = obj['speakerRank']
        self.speaker_name = obj['speakerName']


class EventNote:
    """An event note"""
    def __init__(self, obj: dict):
        self.type = obj.get('type')
        self.title = obj['title']
        self.description = obj['description']
        self.rank = obj['rank']


class EventSchedule:
    """An event schedule item"""
    def __init__(self, obj: dict):
        self.type = obj.get('type')
        self.date_begin = dateutil.parser.parse(obj['dateBegin']) if obj['dateBegin'] is not None else None
        self.date_end = dateutil.parser.parse(obj['dateEnd']) if obj['dateEnd'] is not None else None
        self.title = obj['title']
        self.subtitle = obj['subtitle']
        self.notes = obj['notes']


class SermonSeries:
    """A single object representing a sermon series"""
    def __init__(self, obj: dict):
        self.type = obj.get('type')
        self.latest = dateutil.parser.parse(obj['latest']) if obj['latest'] is not None else None
        self.earliest = dateutil.parser.parse(obj['earliest']) if obj['earliest'] is not None else None
        self.title = obj['title']
        self.count = obj['count']

    def __str__(self):
        return f'{self.title} ({self.count} sermons)'


class SermonEventType:
    """A single object representing a sermon event type"""
    def __init__(self, obj: dict):
        self.type = obj.get('type')
        self.description = obj.get('description')
        self.number_of_sermons = obj.get('numberOfSermons')
        self.roku_image = obj.get('rokuImage')
        self.roku_image_url = obj.get('rokuImageURL')
        self.fire_tv_image = obj.get('fireTVImage')
        self.fire_tv_image_url = obj.get('fireTVImageURL')


class SpurgeonDevotionalType(Enum):
    AM = 'AM'  # Morning Devotional
    PM = 'PM'  # Evening Devotional
    CHECKBOOK = 'CHECKBOOK'  # Faith's Checkbook (note American spelling)


class SpurgeonDevotional:
    """An instance of a Spurgeon devotional"""
    def __init__(self, obj: dict):
        self.type = SpurgeonDevotionalType(obj.get('type'))
        self.month = obj['month']
        self.day = obj['day']
        self.type = obj['type']
        self.quote = obj['quote']
        self.reference = obj['reference']
        self.content = obj['content']
        self.audio = Sermon(obj['audio'])
