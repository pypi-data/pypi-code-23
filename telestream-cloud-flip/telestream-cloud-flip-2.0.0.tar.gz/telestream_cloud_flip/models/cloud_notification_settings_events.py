# coding: utf-8

"""
    Flip API

    Description  # noqa: E501

    OpenAPI spec version: 2.0.0
    Contact: cloudsupport@telestream.net
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class CloudNotificationSettingsEvents(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'encoding_completed': 'bool',
        'encoding_progress': 'bool',
        'video_created': 'bool',
        'video_encoded': 'bool'
    }

    attribute_map = {
        'encoding_completed': 'encoding_completed',
        'encoding_progress': 'encoding_progress',
        'video_created': 'video_created',
        'video_encoded': 'video_encoded'
    }

    def __init__(self, encoding_completed=None, encoding_progress=None, video_created=None, video_encoded=None):  # noqa: E501
        """CloudNotificationSettingsEvents - a model defined in Swagger"""  # noqa: E501

        self._encoding_completed = None
        self._encoding_progress = None
        self._video_created = None
        self._video_encoded = None
        self.discriminator = None

        self.encoding_completed = encoding_completed
        self.encoding_progress = encoding_progress
        self.video_created = video_created
        self.video_encoded = video_encoded

    @property
    def encoding_completed(self):
        """Gets the encoding_completed of this CloudNotificationSettingsEvents.  # noqa: E501

        If set to `true`, a notification will be sent after an encoding becomes complete.  # noqa: E501

        :return: The encoding_completed of this CloudNotificationSettingsEvents.  # noqa: E501
        :rtype: bool
        """
        return self._encoding_completed

    @encoding_completed.setter
    def encoding_completed(self, encoding_completed):
        """Sets the encoding_completed of this CloudNotificationSettingsEvents.

        If set to `true`, a notification will be sent after an encoding becomes complete.  # noqa: E501

        :param encoding_completed: The encoding_completed of this CloudNotificationSettingsEvents.  # noqa: E501
        :type: bool
        """
        if encoding_completed is None:
            raise ValueError("Invalid value for `encoding_completed`, must not be `None`")  # noqa: E501

        self._encoding_completed = encoding_completed

    @property
    def encoding_progress(self):
        """Gets the encoding_progress of this CloudNotificationSettingsEvents.  # noqa: E501

        If set to `true`, a notification will be sent after an encoding's progess changes.  # noqa: E501

        :return: The encoding_progress of this CloudNotificationSettingsEvents.  # noqa: E501
        :rtype: bool
        """
        return self._encoding_progress

    @encoding_progress.setter
    def encoding_progress(self, encoding_progress):
        """Sets the encoding_progress of this CloudNotificationSettingsEvents.

        If set to `true`, a notification will be sent after an encoding's progess changes.  # noqa: E501

        :param encoding_progress: The encoding_progress of this CloudNotificationSettingsEvents.  # noqa: E501
        :type: bool
        """
        if encoding_progress is None:
            raise ValueError("Invalid value for `encoding_progress`, must not be `None`")  # noqa: E501

        self._encoding_progress = encoding_progress

    @property
    def video_created(self):
        """Gets the video_created of this CloudNotificationSettingsEvents.  # noqa: E501

        If set to `true`, a notification will be sent after a video is created.  # noqa: E501

        :return: The video_created of this CloudNotificationSettingsEvents.  # noqa: E501
        :rtype: bool
        """
        return self._video_created

    @video_created.setter
    def video_created(self, video_created):
        """Sets the video_created of this CloudNotificationSettingsEvents.

        If set to `true`, a notification will be sent after a video is created.  # noqa: E501

        :param video_created: The video_created of this CloudNotificationSettingsEvents.  # noqa: E501
        :type: bool
        """
        if video_created is None:
            raise ValueError("Invalid value for `video_created`, must not be `None`")  # noqa: E501

        self._video_created = video_created

    @property
    def video_encoded(self):
        """Gets the video_encoded of this CloudNotificationSettingsEvents.  # noqa: E501

        If set to `true`, a notification will be sent after a video is encoded.  # noqa: E501

        :return: The video_encoded of this CloudNotificationSettingsEvents.  # noqa: E501
        :rtype: bool
        """
        return self._video_encoded

    @video_encoded.setter
    def video_encoded(self, video_encoded):
        """Sets the video_encoded of this CloudNotificationSettingsEvents.

        If set to `true`, a notification will be sent after a video is encoded.  # noqa: E501

        :param video_encoded: The video_encoded of this CloudNotificationSettingsEvents.  # noqa: E501
        :type: bool
        """
        if video_encoded is None:
            raise ValueError("Invalid value for `video_encoded`, must not be `None`")  # noqa: E501

        self._video_encoded = video_encoded

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, CloudNotificationSettingsEvents):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
