"""Channels API"""
from urllib.parse import quote

from open_discussions_api.base import BaseApi
from open_discussions_api.channels.constants import CHANNEL_ATTRIBUTES, VALID_CHANNEL_TYPES


class EmptyAttributesError(AttributeError):
    """Error for empty attributes"""
    pass


class UnsupportedAttributeError(AttributeError):
    """Error for an unsupported attribute"""
    pass


class InvalidChannelTypeError(AttributeError):
    """Error for invalid channel type"""
    pass


class ChannelsApi(BaseApi):
    """Channels API"""

    def create(self, **channel_params):
        """
        Create a new channel

        Args:
            channel_params (dict):
                Attributes used in creation of the channel, see CHANNEL_ATTRIBUTES for a list

        Returns:
            requests.Response:
                The response to the channel creation. If successful it contains the payload with
                the new channel's parameters.
        """
        if not channel_params:
            raise EmptyAttributesError()

        for key in channel_params:
            if key not in CHANNEL_ATTRIBUTES:
                raise UnsupportedAttributeError("Argument '{}' is not a supported field".format(key))

        if channel_params['channel_type'] not in VALID_CHANNEL_TYPES:
            raise InvalidChannelTypeError(
                "Channel type '{}' is not a valid option".format(channel_params['channel_type'])
            )

        return self.session.post(
            self.get_url("/channels/"),
            json=channel_params
        )

    def add_contributor(self, channel_name, username):
        """
        Add a contributor to a channel

        Args:
            channel_name (str): The name of the channel
            username (str): The username of the contributor

        Returns:
            requests.Response:
                The response of the request to add a contributor. This should only
                contain the contributor's username in its payload, similar to the request payload.
        """

        return self.session.post(
            self.get_url("/channels/{channel_name}/contributors/".format(
                channel_name=quote(channel_name),
            )),
            json={"contributor_name": username}
        )

    def remove_contributor(self, channel_name, username):
        """
        Remove a contributor from a channel

        Args:
            channel_name (str): The name of the channel
            username (str): The username of the contributor to be removed

        Returns:
            requests.Response: The response of the request to delete the contributor
        """

        return self.session.delete(
            self.get_url("/channels/{channel_name}/contributors/{username}/".format(
                channel_name=quote(channel_name),
                username=quote(username),
            ))
        )

    def add_moderator(self, channel_name, username):
        """
        Add a moderator to a channel

        Args:
            channel_name (str): The name of the channel
            username (str): The name of the user to add as moderator

        Returns:
            requests.Response: The response of the request to add a moderator. This should only
            contain the moderator username, the same which was passed in the request.
        """
        return self.session.post(
            self.get_url("/channels/{channel_name}/moderators/".format(
                channel_name=quote(channel_name)
            )),
            json={"moderator_name": username},
        )

    def remove_moderator(self, channel_name, username):
        """
        Remove a moderator from a channel

        Args:
            channel_name (str): The name of the channel
            username (str): The name of the moderator to remove

        Returns:
            request.Response: The response of the request to remove the moderator
        """
        return self.session.delete(
            self.get_url("/channels/{channel_name}/moderators/{username}/".format(
                channel_name=quote(channel_name),
                username=quote(username),
            ))
        )

    def add_subscriber(self, channel_name, username):
        """
        Add a subscriber to a channel

        Args:
            channel_name (str): The name of the channel
            username (str): The username of the subscriber

        Returns:
            requests.Response:
                The response of the request to add a subscriber.
        """
        return self.session.post(
            self.get_url("/channels/{channel_name}/subscribers/".format(
                channel_name=quote(channel_name),
            )),
            json={"subscriber_name": username}
        )

    def remove_subscriber(self, channel_name, username):
        """
        Remove a subscriber from a channel

        Args:
            channel_name (str): The name of the channel
            username (str): The username of the subscriber

        Returns:
            requests.Response:
                The response of the request to add a subscriber
        """
        return self.session.delete(
            self.get_url("/channels/{channel_name}/subscribers/{username}/".format(
                channel_name=quote(channel_name),
                username=quote(username),
            ))
        )
