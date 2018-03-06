''' Crackle API Wrapper '''
# pylint: disable=too-few-public-methods,no-member
from __future__ import print_function
import time
from datetime import datetime, date
from random import shuffle
from collections import namedtuple
import json
import requests
from crackle_api_helpers.authentication.authentication import Authentication
from crackle_api_helpers.authentication.authentication_helpers import generate_username
from crackle_api_helpers import AuthKeyMissingError, SESSION


def default_configuration():
    """ Get a default configuration """
    host = ''
    partner_id = ''
    secret = ''
    geo_code = 'US'

    apiconfig = namedtuple('apiconfig',
                           'host partner_id secret geo_code')
    return apiconfig(
        host=host,
        partner_id=partner_id,
        secret=secret,
        geo_code=geo_code)


class AuthHelpers(object):
    """
    Authentication methods
    """
    def __init__(self, configuration=None):
        if not configuration:
            self.configuration = default_configuration()
        else:
            self.configuration = configuration

    def register_config(self):
        '''
        GET /Service.svc/register/config
        '''
        endpoint = '/Service.svc/register/config'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            return response
        except ValueError as exception:
            print(exception)


    def register_quick(self):
        '''
        POST /Service.svc/register/quick
        on success:
            return data(message_code, email_address, password, user_id)
        on failure:
            return data(message_code, "", "", "", "")

        '''
        endpoint = '/Service.svc/register/quick'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)

        email_domain = 'gmail.com'
        password = 'kyqkuBmn4'
        dob = '01012000'
        email_address = generate_username('AUTO_JAN_API_') + '@' + email_domain

        data = {
            "emailAddress": email_address,
            "password": password,
            "dob": dob,
            "sendNewsletter": True
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            data = namedtuple(
                "data", ["message_code", "email", "password", "user_id"])
            response_text = json.loads(response.content)
            user_id = response_text['userID']
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return data(message_code, email_address, password, user_id)
            return data(message_code, "", "", "")
        except ValueError as exception:
            print(exception)


    def login(self, email_address, password):
        '''
        POST /Service.svc/login
        on success:
            return data(message_code, email_address, password, user_id)
        on failure:
            return data(message_code, "", "", "", "")
        '''
        endpoint = '/Service.svc/login'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)

        affiliate_user_id = 'e2468342-3071-411c-9d3c-7eb8d7cd4d8c'

        data = {
            "emailAddress": email_address,
            "password": password,
            "geoCode": self.configuration.geo_code,
            "AffiliateUserId": affiliate_user_id
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            data = namedtuple(
                "data", ["message_code", "email", "password", "user_id"])
            response_text = json.loads(response.content)
            user_id = response_text['userID']
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return data(message_code, email_address, password, user_id)
            return data(message_code, "", "", "")
        except ValueError as exception:
            print(exception)

    def logout(self, user_id):
        '''
        POST /Service.svc/logout
        on success:
            return True
        '''
        endpoint = '/Service.svc/logout?userId={}'.format(user_id)
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.post(path)
        try:
            response_text = json.loads(response.content)
            message_code = response_text['messageCodeDescription']
            if 'OK' in message_code:
                return True
            return False
        except ValueError as exception:
            print(exception)

    def deactivate(self, user_id):
        '''
        POST /Service.svc/deactivate
        on success:
            return True
        '''
        endpoint = '/Service.svc/deactivate'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.post(path)

        data = {
            "userId": user_id,
            "reason": 0,
            "comment": ""
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            response_text = json.loads(response.content)
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return True
            return False
        except ValueError as exception:
            print(exception)


class APIWrapperHelpers(object):
    """
    Helper methods for API wrapper
    """

    def __init__(self, configuration):
        self.configuration = configuration

    @staticmethod
    def wait_between_requests():
        ''' time to wait in seconds between HTTP requests '''
        time.sleep(0.25)

    def _get_valid_curations(self):
        ''' Returns a list of valid curations '''
        endpoint = '/Service.svc/curation/homepage/false/{}'.format(
            self.configuration.geo_code)

        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            curations = response_text['Result']['Slots']
            return [curation['Id'] for curation in curations]
        except ValueError as exception:
            print(exception)

    def get_curation_by_slot_number(self, slot_position, auth=True):
        ''' Returns the curation at a given slot position '''
        endpoint = '/Service.svc/curation/homepage/false/{}'.format(
            self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            curations = response_text['Result']['Slots']
            return [curation for curation in curations if curation['SlotPosition'] == slot_position][0]
        except ValueError as exception:
            print(exception)

    def get_curation_titles(self, curation_id, auth=True):
        ''' Returns a list of all asset titles in a given curation '''
        media_titles = []
        endpoint = '/Service.svc/curation/{0}/{1}'.format(
            curation_id, self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            media_items = response_text['Result']['Items']
            for media_item in media_items:
                media_titles.append(media_item['MediaInfo'].get('Title'))
            return media_titles
        except ValueError as exception:
            print(exception)

    def get_valid_media_ids(self):
        ''' Returns a randomised list of valid media IDs '''
        curation_ids = self._get_valid_curations()
        media_ids = []

        for curation_id in curation_ids:
            endpoint = '/Service.svc/curation/{0}/{1}'.format(
                curation_id, self.configuration.geo_code)

            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                response_text = json.loads(response.content)
                media_items = response_text['Result']['Items']
                for media_item in media_items:
                    media_ids.append(media_item['MediaInfo'].get('Id'))
            except ValueError as exception:
                print(exception)
            APIWrapperHelpers.wait_between_requests()
        shuffle(media_ids)
        return media_ids

    def get_media_id_metadata(self, media_id):
        """
        Get the metadata for a video (media_id)
        return: json response if successful
                False if the video does not exist or has expired
        """
        endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                    .format(media_id, self.configuration.geo_code))

        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            if not response.status_code == requests.codes.ok:
                print('Asset did not respond with HTTP OK')
                return False
            response_text = json.loads(response.content)
            expiry_time = response_text['RightsExpirationDate']

            expiry_time = datetime.strptime(expiry_time, "%m/%d/%Y %I:%M:%S %p")
            if expiry_time < datetime.now():
                print('Asset has expired')
                return False
            return response_text if response_text else False
        except ValueError as exception:
            print(exception)


class APIWrapper(AuthHelpers):
    """
    Crackle API Wrapper methods
    """
    def __init__(self, configuration=None):
        if not configuration:
            self.configuration = default_configuration()
        else:
            self.configuration = configuration
        self.api_helpers = APIWrapperHelpers(self.configuration)
        self.media_ids = self.api_helpers.get_valid_media_ids()

    def find_media(self):
        '''
        Find any media item
        returns: ('media_id', 'short_name', 'media_duration')
        '''
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))
            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                duration_in_seconds = response_text['DurationInSeconds']
                print('found media item')
                data = namedtuple(
                    "data", ["media_id", "short_name", "duration_in_seconds"])
                return data(media_id, short_name, duration_in_seconds)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media item was found')
        return None

    def find_media_without_adverts(self):
        '''
        Find a media item without any adverts
        returns: ('media_id', 'short_name', 'media_duration')
        '''
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                duration_in_seconds = response_text['DurationInSeconds']
                chapters = response_text['Chapters']
                if not chapters:
                    print('found media with no adverts')
                    data = namedtuple(
                        "data", ["media_id", "short_name", "duration_in_seconds"])
                    return data(media_id, short_name, duration_in_seconds)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items without adverts were found')
        return None

    def find_media_with_preroll(self):
        '''
        Find a media item with a preroll
        returns: ('media_id', 'short_name')
        '''
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    continue
                response_text = json.loads(response.content)
                chapters = response_text['Chapters']
                if not chapters:
                    continue
                pre_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'pre-roll']
                if not pre_rolls:
                    continue
                print('found media with pre-roll')
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items with a preroll were found')
        return None

    def find_media_without_preroll(self):
        '''
        Find a media item without a preroll
        returns: ('media_id', 'short_name')
        '''
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                chapters = response_text['Chapters']
                if not chapters:
                    print('found media with no pre-roll (no adverts)')
                    return data(media_id, short_name)
                pre_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'pre-roll']
                if not pre_rolls:
                    print('found media with no pre-roll (has mid-rolls)')
                    return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items without a preroll were found')
        return None

    def find_media_with_two_midrolls(self):
        '''
        Find a media item with at least two midrolls
        returns: ('media_id', 'short_name', [midroll timestamps (seconds)])
        '''
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    continue
                response_text = json.loads(response.content)
                short_name = \
                        response_text['ParentChannelDetailsSummary']['ShortName']
                chapters = response_text['Chapters']
                if not chapters:
                    continue
                mid_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'']
                if not len(mid_rolls) >= 2:
                    continue
                print('found media with at least two midrolls')
                mid_roll_timestamps = \
                    [ad['StartTimeInMilliSeconds'] / 1000 for ad in mid_rolls]
                data = namedtuple(
                    "data", ["media_id", "short_name", "mid_roll_timestamps"])
                return data(media_id, short_name, mid_roll_timestamps)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items with at least two midrolls were found')
        return None

    def find_media_with_rating(self, rating='Not Rated'):
        '''
        Find a media item with the given rating
        rating: 'Not Rated', 'PG' 'PG-13', 'TV-14', 'R'
        returns: ('media_id', 'short_name')

        '''
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                rating_result = response_text['Rating']
                if rating != rating_result:
                    continue
                print('found media matching the provided rating')
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items matching the provided rating were found')
        return None

    def find_media_with_min_duration(self, min_duration_mins=1):
        '''
        Find a media item with the minimum duration
        min_duration: minimum duration in minutes
        returns: ('media_id', 'short_name')

        '''
        min_duration = min_duration_mins * 60
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    continue
                response_text = json.loads(response.content)
                short_name = \
                        response_text['ParentChannelDetailsSummary']['ShortName']
                media_duration = response_text['DurationInSeconds']
                if int(media_duration) < min_duration:
                    continue
                print('found media item matching the minimum duration')
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items matching the minimum required duration found')
        return None
