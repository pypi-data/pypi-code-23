# coding=utf-8
"""

This module is the implementation of tweepy.StreamListener.

This includes handling several events like getting a status through
the stream, getting a TweepError, getting an exception, or
connecting/disconnecting to the stream.

"""

import logging

from tweepy import StreamListener


# This class implements tweepy.StreamListener events.
class Listener(StreamListener):
    """ This class implements every tweepy.StreamListener event.

    This class handles data, error, exception connection and disconnection events.

    Attributes:
    ----------
    batcher : Batcher
        The batcher instance for batch processing.

    """
    def __init__(self, batcher):
        """
        Initializer for Listener class.


        Parameters
        ----------
        batcher : Batcher
            The Batcher object.

        """
        self.batcher = batcher
        logging.basicConfig(filename='twitter_log.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        super(Listener, self).__init__()

    def on_status(self, status):
        """
        This function handles status when it is collected from stream.


        Parameters
        ----------
        status : tweepy.Status
            The collected status object.

        Returns
        -------

        """
        self.batcher.handle_status(status, self.batcher.config)

    def on_connect(self):
        """
        This function handles when stream is connected.


        Parameters
        ----------

        Returns
        -------

        """
        logging.getLogger("connection").info("connection established.")

    def on_disconnect(self, notice):
        """
        This function handles when stream disconnects.


        Parameters
        ----------
        notice : str
            The disconnection notice.

        Returns
        -------

        """
        logging.getLogger("connection").info("connection interrupted: " + notice)

    def on_limit(self, track):
        """
        This function handles when rate limit is hit.


        Parameters
        ----------
        track : int
            The total number of undelivered tweets.

        Returns
        -------

        """
        logging.getLogger("limit").info("track limit notice on track: " + str(track))

    def on_delete(self, status_id, user_id):
        """
        This function handles when tweet is deleted.


        Parameters
        ----------
        status_id : int
            The deleted tweet id.
        user_id : int
            The deleted tweet author id.

        Returns
        -------

        """
        logging.getLogger("delete").info("deleted tweet with id: " + str(status_id))

    def on_error(self, status_code):
        """
        This function handles when error occurs.


        Parameters
        ----------
        status_code : int
            The error code.

        Returns
        -------

        """
        logging.getLogger("error").info("error: " + str(status_code))