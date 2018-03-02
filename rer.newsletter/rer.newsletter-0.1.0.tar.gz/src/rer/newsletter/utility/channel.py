# -*- coding: utf-8 -*-
from zope.interface import Interface


# general
UNHANDLED = 0
SUBSCRIBED = OK = 1
INVALID_CHANNEL = 5

# subscribe
ALREADY_SUBSCRIBED = 2
INVALID_EMAIL = 3

# Email
PROBLEM_WITH_MAIL = 11

# unsubscribe
INEXISTENT_EMAIL = 4

# add channel
CHANNEL_USED = 6

# import usersList
FILE_FORMAT = 7

# delete user
MAIL_NOT_PRESENT = 8

# user's activation
ALREADY_ACTIVE = 9
INVALID_SECRET = 10


class IChannelUtility(Interface):

    def activateUser(channel, secret):
        """
        Activate user from confirmation email.

        Args:
            channel (str): channel id,
            secret (str): token for activation

        Returns:
            int: OK (1) if succesful,
                 ALREADY_ACTIVE (9),
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_SECRET (10) problem with secret,
                 PROBLEM_WITH_MAIL (11) if errors are
                 present when email is sent.

        Raises:
        """

    def addUser(channel, mail):
        """
        Add user to channel from Admin side

        Args:
            channel (str): channel id,
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 ALREADY_SUBSCRIBED (2),
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_EMAIL (3) problem with mail.

        Raises:
        """

    def subscribe(channel, mail):
        """
        Subscribe user to channel and return secret
        that needs for user confirmation.

        Args:
            channel (str): channel id
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 ALREADY_SUBSCRIBED (2),
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_EMAIL (3) problem with mail.
            str: secret for autenticate user.

        Raises:
        """

    def unsubscribe(channel, mail):
        """
        Unsubscribe user to channel and return a secret
        that needs for user confirmation for delete.

        Args:
            channel (str): channel id
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found,
                 INEXISTENT_MAIL (4) mail not found.
            str: secret for delete user.

        Raises:
        """

    def sendMessage(channel, message, unsubscribe_footer=None):
        """
        Send message

        Args:
            channel (str): channel id
            message (datastream): message
            unsubscribe_footer (template): template for unsubscribe link to
                                           newsletter

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found.

        Raises:
        """

    def getNumActiveSubscribers(channel):
        """
        Return number of active subscribers for channel.

        Args:
            channel (str): channel id

        Returns:
            (number of subscribers and status together)
            int: number of active subscribers and OK (1) if succesful,
                 INVALID_CHANNEL (5) and None if channel not found.

        Raises:
        """

    def addChannel(channel):
        """
        add new channel.

        Args:
            channel (str): channel id

        Returns:
            int: OK (1) if succesful,
                 CHANNEL_USED (6) channel already used.

        Raised:
        """

    def importUsersList(channel, usersList):
        """
        import list of email from CSV file.

        Args:
            channel (str): channel id
            usersList (list): email

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_EMAIL (3) user's email not found.

        Raised:
        """

    def emptyChannelUsersList(channel):
        """
        empties channel users list.

        Args:
            channel (str): channel id

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found.

        Raised:
        """

    def deleteUser(channel, email, secret):
        """
        delete a user from channel with or secret.

        Args:
            email (str): email
            channel (str): channel id
            secret (str): token for delete confirmation

        Returns:
            int OK (1) if succesful,
                INVALID_CHANNEL (5) channel not found,
                MAIL_NOT_PRESENT (8) mail not present,
                PROBLEM_WITH_MAIL (11) if errors are
                present when email is sent.

        Raised:
        """

    def deleteUserList(channel, usersList):
        """
        delete a usersList from channel.

        Args:
            usersList (list): email
            channel (str): channel id

        Returns:
            int OK (1) if succesful,
            INVALID_CHANNEL (5) channel not found,
        """

    def exportUsersList(channel):
        """
        export all user of channel

        Args:
            channel (str): channel id

        Returns:
            (List and Status together)
            List of email and OK if succesful,
            None and Int INVALID_CHANNEL (5) if channel not found.

        Raised:
        """
