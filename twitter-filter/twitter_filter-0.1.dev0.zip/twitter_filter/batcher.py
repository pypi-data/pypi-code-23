# coding=utf-8
"""

This module provides the batching functionalities for tweets info
batching every hour or day and getting the collected tweets reactions
(favourites and retweets count).

"""

import re
from datetime import datetime, timedelta
from os import listdir
from os.path import isfile, join

from twitter_filter.dates_handler import DatesHandler
from twitter_filter.exceptions_wrapper import ErrorWrapper
from twitter_filter.file_util import FileUtil

from twitter_filter.twitter_api import TwitterApiWrapper


# This class is the main batching class.
class Batcher(object):
    """ This class is responsible for batching tweets on hourly and daily basis.

    It gets the tweet, the batch requested location on file system, and stores the
    resultant batches in files on file system.

    Attributes:
    ----------
    hourly_start_time : time
        The hourly batch start time.
    hourly_elapsed_time : int
        The hourly elapsed time in milli seconds.
    daily_start_time : time
        The daily batch start time.
    daily_elapsed_time : int
        The daily elapsed time in milli seconds.
    location : str
        The batch requested location in file system.
    statuses : list
        The statuses batch.
    days_range : int
        The number of previous days to look for when collecting reactions (favourites and retweets).
    config : str
        The application keys file path (for reactions collection).

    """
    def __init__(self, start_time, location, days_range, config, batcher=None):
        """
        Initializer for StatusParser class.


        Parameters
        ----------
        start_time : datetime
            The batch start time.
        location : str
            The batch requested location in file system.
        days_range : int
            The number of previous days to look for when collecting reactions (favourites and retweets).
        batcher : Batcher or None
            The copy constructor object.
        config : str
            The application keys file path (for reactions collection).

        """
        try:
            if batcher is None:
                self.daily_start_time = start_time
                self.hourly_start_time = start_time
                self.hourly_elapsed_time = 0
                self.daily_elapsed_time = 0
                self.location = location
                self.days_range = days_range
                self.config = config
                self.statuses = [[] for x in range(15)]
            else:
                self.daily_start_time = batcher.daily_start_time
                self.hourly_start_time = batcher.hourly_start_time
                self.hourly_elapsed_time = batcher.hourly_elapsed_time
                self.daily_elapsed_time = batcher.daily_elapsed_time
                self.location = batcher.location
                self.days_range = batcher.days_range
                self.config = batcher.config
                self.statuses = batcher.statuses
        except Exception as e:
            ErrorWrapper(e).handle()

    def handle_status(self, status, config):
        """
        This function either stores the status in the statuses list or calls
        handle_batching depending on the time elapsed.


        Parameters
        ----------
        status : tweepy.Status
            The status to handle.
        config : str
            The application keys file path (for reactions collecting).

        Returns
        -------

        """
        try:
            clock = datetime.now()
            if self.hourly_elapsed_time < 60:
                self.parse(status)
                #print(self.hourly_elapsed_time)
                self.hourly_elapsed_time = (clock - self.hourly_start_time).total_seconds()/60
                self.daily_elapsed_time = (clock - self.daily_start_time).days
            else:
                self.hourly_elapsed_time = 0
                self.hourly_start_time = clock
                self.handle_batching()
                if self.daily_elapsed_time > 3:
                    self.daily_elapsed_time = 0
                    self.daily_start_time = clock
                    self.handle_reactions(config, self.days_range)
        except Exception as e:
            ErrorWrapper(e).handle()

    def handle_batching(self):
        """
        This function writes the statuses list in the file system.


        Parameters
        ----------

        Returns
        -------

        """
        try:
            for i in range(0, 15, 1):
                store_path = self.location+"/"+str(i+1)+"/"+str(datetime.today().date())+"/"+str(datetime.now().time().hour) + "__" + str(i)+".txt"
                FileUtil.write_to_file_chunks(store_path, self.statuses[i], 500)
                self.statuses[i] = []
        except Exception as e:
            ErrorWrapper(e).handle()

    def handle_reactions(self, config, days_range):
        """
        This function gets the favourites and retweets count and writes them in file system.


        Parameters
        ----------
        config : str
            The Twitter application configuration file path.
        days_range : int
            The previous days range to get.

        Returns
        -------

        """
        try:
            (favourites_count, retweets_count) = self.get_reactions(config, days_range)
            today = datetime.today()
            dates = DatesHandler(today, today - timedelta(days_range)).date_range()
            i = self.days_range
            for date in dates:
                favourites_files_path = self.location + "/16/" + str(date.date()) + "/"
                retweets_files_path = self.location + "/17/" + str(date.date()) + "/"
                for j in range(len(favourites_count[i])):
                    FileUtil.write_to_file_chunks(favourites_files_path+favourites_count[i][j]["index"], favourites_count[i][j]["data"], 500)
                    FileUtil.write_to_file_chunks(retweets_files_path + retweets_count[i][j]["index"], retweets_count[i][j]["data"], 500)
                i = i + 1
        except Exception as e:
            ErrorWrapper(e).handle()

    def get_ids(self, days_range):
        """
        This function gets the statuses ids for tweets which came days_range days ago.


        Parameters
        ----------
        days_range : int
            The number of days range to count back.

        Returns
        -------
        ids : list
            The days_range previous days tweets' ids.

        """
        try:
            today = datetime.today()
            ids = []
            dates = DatesHandler(today, today - timedelta(days_range)).date_range()
            for date in dates:
                day_ids = []
                only_files = [f for f in listdir(self.location+"/1/"+str(date.date())) if isfile(join(self.location+"/1/"+str(date.date()), f))]
                for f in only_files:
                    hour_ids = {"data": FileUtil.file_reader(self.location + "/1/" + str(date.date()) + "/" + f),
                                "index": f}
                    day_ids.append(hour_ids)
                ids.append(day_ids)
            return ids
        except Exception as e:
            ErrorWrapper(e).handle()

    def get_reactions(self, config, days_range):
        """
        This function gets the favourites and retweets count for them to store in file system.


        Parameters
        ----------
        config : str
            The Twitter application configuration file path.
        days_range : int
            The number of days range to count back.

        Returns
        -------
        favourites_count : list
            A list of favourites count for every collected tweet in the past days_range days.
        retweets_count : list
            A list of retweets count for every collected tweet in the past days_range days.

        """
        try:
            ids = self.get_ids(days_range)
            favourites_count = []
            retweets_count = []
            api = TwitterApiWrapper(config)
            for day in ids:
                day_favourites = []
                day_retweets = []
                for hour in day:
                    hour_favourites = {"data": [], "index": ""}
                    hour_retweets = {"data": [], "index": ""}
                    for tweet_id in hour["data"]:
                        hour_favourites["data"].append(str(api.get_favourites(tweet_id)))
                        hour_retweets["data"].append(str(api.get_retweets(tweet_id)))
                    hour_favourites["index"] = hour["index"]
                    hour_retweets["index"] = hour["index"]
                    day_favourites.append(hour_favourites)
                    day_retweets.append(hour_retweets)
                favourites_count.append(day_favourites)
                retweets_count.append(day_retweets)
            return favourites_count, retweets_count
        except Exception as e:
            ErrorWrapper(e).handle()

    def parse(self, status):
        """
        This function parses the Status object and adds every attribute in its suitable partial list.


        Parameters
        ----------
        status : tweepy.Status
            The status to parse.

        Returns
        -------

        """
        try:
            text = status.text
            text = re.sub(u"\n", u" ", text)
            text = re.sub(u"\\s+", u" ", text)
            self.statuses[0].append(str(status.id))
            self.statuses[1].append(text)
            if hasattr(status, 'retweeted_status'):
                self.statuses[2].append(str(True))
                self.statuses[7].append(str(status.retweeted_status.id))
                self.statuses[8].append(str(status.retweeted_status.user.screen_name))
                self.statuses[9].append(str(status.retweeted_status.retweet_count))
                self.statuses[10].append(str(status.retweeted_status.favorite_count))
            else:
                self.statuses[2].append(str(False))
                self.statuses[7].append(str(None))
                self.statuses[8].append(str(None))
                self.statuses[9].append(str(None))
                self.statuses[10].append(str(None))
            if hasattr(status, 'place') and hasattr(status.place, 'country_code'):
                self.statuses[3].append(str(status.place.country_code))
            else:
                self.statuses[3].append(str(None))
            self.statuses[4].append(str(status.created_at))
            self.statuses[5].append(str(status.user.id))
            self.statuses[6].append(str(status.user.screen_name))
            self.statuses[11].append(str(len(status.entities['urls'])))
            self.statuses[12].append(str(len(status.entities['hashtags'])))
            self.statuses[13].append(str(status.user.followers_count))
            self.statuses[14].append(str(status.user.friends_count))
        except Exception as e:
            ErrorWrapper(e).handle()
            