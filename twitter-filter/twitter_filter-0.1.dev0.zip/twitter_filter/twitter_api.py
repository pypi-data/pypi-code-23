# coding=utf-8
"""

This module is responsible for providing the api instances and methods.

This includes configuring the twitter app keys and secrets, creating stream
or search api instances and filtering on keywords.

"""

from twitter_filter.file_util import FileUtil
from tweepy import OAuthHandler, API, StreamListener, Stream

from twitter_filter.exceptions_wrapper import ErrorWrapper, ParametersError


# This class provides twitter-api functionalities.
class TwitterApiWrapper(object):
    """ This class implements every twitter data collecting related functionality.

    This class creates twitter api instances and performs some data acquisition operations.

    Attributes:
    ----------
    config_file_path : str
        The application's keys file path.
    listener_class : str
        The listener implementation class name.

    """
    def __init__(self, config_file_path, listener_class=None):
        """
        Initializer for TwitterApiWrapper class.


        Parameters
        ----------
        config_file_path : str
            The application's keys file path.
        listener_class : object or None
            The listener implementation class name.

        """
        try:
            self.config = config_file_path
            if listener_class is not None:
                if listener_class.__class__.__bases__[0] is StreamListener:
                    self.listener = listener_class
                else:
                    raise ParametersError(Exception("wrong parameters class type"), 50)
        except ParametersError as e:
            print(ErrorWrapper(e.ex, e.code).handle())

    def build_api(self):
        """
        This function builds the api instance using the config attribute.


        Parameters
        ----------

        Returns
        -------
        Api
            The twitter API instance.

        """
        try:
            config = FileUtil.file_reader(self.config)
            auth = OAuthHandler(config[0], config[1])
            auth.set_access_token(config[2], config[3])
            return API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5, retry_errors=5)
        except Exception as e:
            print(ErrorWrapper(e).handle())

    def get_stream_api_instance(self):
        """
        This function builds a streaming api instance using the api instance.


        Parameters
        ----------

        Returns
        -------
        Stream
            The twitter streaming API instance.

        """
        try:
            api_instance = self.build_api()
            stream = Stream(auth=api_instance.auth, listener=self.listener)
            return stream
        except Exception as e:
            print(ErrorWrapper(e).handle())

    def filter(self, keywords, stream, languages=None):
        """
        This function opens a connection with Twitter and starts to filter
        tweets coming from the stream on Keywords list.


        Parameters
        ----------
        keywords : list
            The keywords to filter on list.
        stream : Stream
            The stream instance.
        languages : list
            The requested tweets language

        Returns
        -------

        """
        try:
            stream.filter(track=keywords, async=True, languages=languages)
        except Exception as e:
            print(ErrorWrapper(e).handle())

    def get_status_obj(self, status_id):
        """
        This function gets the status using its ID.


        Parameters
        ----------
        status_id : int
            The status ID.

        Returns
        -------
        Status
            The resulting Status object.

        """
        try:
            api = self.build_api()
            return api.get_status(status_id)
        except Exception as e:
            ErrorWrapper(e).handle()

    def get_favourites(self, status_id):
        """
        This function gets the status's favourites count using its ID.


        Parameters
        ----------
        status_id : int
            The status ID.

        Returns
        -------
        int
            The status favourites count.

        """
        try:
            s = self.get_status_obj(status_id)
            if s is not None:
                return s.favorite_count
            else:
                return -1
        except Exception as e:
            ErrorWrapper(e).handle()

    def get_retweets(self, status_id):
        """
        This function gets the status's retweeting count using its ID.


        Parameters
        ----------
        status_id : int
            The status ID.

        Returns
        -------
        int
            The status retweeting count.

        """
        try:
            s = self.get_status_obj(status_id)
            if s is not None:
                return s.retweet_count
            else:
                return -1
        except Exception as e:
            ErrorWrapper(e).handle()

    def get_user(self, status_id):
        """
        This function gets the status author User's object.


        Parameters
        ----------
        status_id : int
            The status ID.

        Returns
        -------
        int
            The status author User's object.

        """
        try:
            s = self.get_status_obj(status_id)
            return s.author
        except Exception as e:
            ErrorWrapper(e).handle()

    def get_followers(self, status_id):
        """
        This function gets the status's author followers count.


        Parameters
        ----------
        status_id : int
            The status ID.

        Returns
        -------
        int
            The status's author followers count.

        """
        try:
            s = self.get_user(status_id)
            return len(s.followers_ids(s.id))
        except Exception as e:
            ErrorWrapper(e).handle()

    def get_friends(self, status_id):
        """
        This function gets the status's author friends count.


        Parameters
        ----------
        status_id : int
            The status ID.

        Returns
        -------
        int
            The status's author friends count.

        """
        try:
            s = self.get_user(status_id)
            return len(s.friends_ids(s.id))
        except Exception as e:
            ErrorWrapper(e).handle()