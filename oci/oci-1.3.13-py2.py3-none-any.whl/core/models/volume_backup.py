# coding: utf-8
# Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.


from ...util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from ...decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class VolumeBackup(object):

    def __init__(self, **kwargs):
        """
        Initializes a new VolumeBackup object with values from values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param compartment_id:
            The value to assign to the compartment_id property of this VolumeBackup.
        :type compartment_id: str

        :param defined_tags:
            The value to assign to the defined_tags property of this VolumeBackup.
        :type defined_tags: dict(str, dict(str, object))

        :param display_name:
            The value to assign to the display_name property of this VolumeBackup.
        :type display_name: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this VolumeBackup.
        :type freeform_tags: dict(str, str)

        :param id:
            The value to assign to the id property of this VolumeBackup.
        :type id: str

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this VolumeBackup.
            Allowed values for this property are: "CREATING", "AVAILABLE", "TERMINATING", "TERMINATED", "FAULTY", "REQUEST_RECEIVED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param size_in_gbs:
            The value to assign to the size_in_gbs property of this VolumeBackup.
        :type size_in_gbs: int

        :param size_in_mbs:
            The value to assign to the size_in_mbs property of this VolumeBackup.
        :type size_in_mbs: int

        :param time_created:
            The value to assign to the time_created property of this VolumeBackup.
        :type time_created: datetime

        :param time_request_received:
            The value to assign to the time_request_received property of this VolumeBackup.
        :type time_request_received: datetime

        :param unique_size_in_gbs:
            The value to assign to the unique_size_in_gbs property of this VolumeBackup.
        :type unique_size_in_gbs: int

        :param unique_size_in_mbs:
            The value to assign to the unique_size_in_mbs property of this VolumeBackup.
        :type unique_size_in_mbs: int

        :param volume_id:
            The value to assign to the volume_id property of this VolumeBackup.
        :type volume_id: str

        """
        self.swagger_types = {
            'compartment_id': 'str',
            'defined_tags': 'dict(str, dict(str, object))',
            'display_name': 'str',
            'freeform_tags': 'dict(str, str)',
            'id': 'str',
            'lifecycle_state': 'str',
            'size_in_gbs': 'int',
            'size_in_mbs': 'int',
            'time_created': 'datetime',
            'time_request_received': 'datetime',
            'unique_size_in_gbs': 'int',
            'unique_size_in_mbs': 'int',
            'volume_id': 'str'
        }

        self.attribute_map = {
            'compartment_id': 'compartmentId',
            'defined_tags': 'definedTags',
            'display_name': 'displayName',
            'freeform_tags': 'freeformTags',
            'id': 'id',
            'lifecycle_state': 'lifecycleState',
            'size_in_gbs': 'sizeInGBs',
            'size_in_mbs': 'sizeInMBs',
            'time_created': 'timeCreated',
            'time_request_received': 'timeRequestReceived',
            'unique_size_in_gbs': 'uniqueSizeInGBs',
            'unique_size_in_mbs': 'uniqueSizeInMbs',
            'volume_id': 'volumeId'
        }

        self._compartment_id = None
        self._defined_tags = None
        self._display_name = None
        self._freeform_tags = None
        self._id = None
        self._lifecycle_state = None
        self._size_in_gbs = None
        self._size_in_mbs = None
        self._time_created = None
        self._time_request_received = None
        self._unique_size_in_gbs = None
        self._unique_size_in_mbs = None
        self._volume_id = None

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this VolumeBackup.
        The OCID of the compartment that contains the volume backup.


        :return: The compartment_id of this VolumeBackup.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this VolumeBackup.
        The OCID of the compartment that contains the volume backup.


        :param compartment_id: The compartment_id of this VolumeBackup.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this VolumeBackup.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.

        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.us-phoenix-1.oraclecloud.com/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this VolumeBackup.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this VolumeBackup.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.

        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.us-phoenix-1.oraclecloud.com/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this VolumeBackup.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    @property
    def display_name(self):
        """
        **[Required]** Gets the display_name of this VolumeBackup.
        A user-friendly name for the volume backup. Does not have to be unique and it's changeable.
        Avoid entering confidential information.


        :return: The display_name of this VolumeBackup.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this VolumeBackup.
        A user-friendly name for the volume backup. Does not have to be unique and it's changeable.
        Avoid entering confidential information.


        :param display_name: The display_name of this VolumeBackup.
        :type: str
        """
        self._display_name = display_name

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this VolumeBackup.
        Free-form tags for this resource. Each tag is a simple key-value pair with no
        predefined name, type, or namespace. For more information, see
        `Resource Tags`__.

        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.us-phoenix-1.oraclecloud.com/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this VolumeBackup.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this VolumeBackup.
        Free-form tags for this resource. Each tag is a simple key-value pair with no
        predefined name, type, or namespace. For more information, see
        `Resource Tags`__.

        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.us-phoenix-1.oraclecloud.com/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this VolumeBackup.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def id(self):
        """
        **[Required]** Gets the id of this VolumeBackup.
        The OCID of the volume backup.


        :return: The id of this VolumeBackup.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this VolumeBackup.
        The OCID of the volume backup.


        :param id: The id of this VolumeBackup.
        :type: str
        """
        self._id = id

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this VolumeBackup.
        The current state of a volume backup.

        Allowed values for this property are: "CREATING", "AVAILABLE", "TERMINATING", "TERMINATED", "FAULTY", "REQUEST_RECEIVED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this VolumeBackup.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this VolumeBackup.
        The current state of a volume backup.


        :param lifecycle_state: The lifecycle_state of this VolumeBackup.
        :type: str
        """
        allowed_values = ["CREATING", "AVAILABLE", "TERMINATING", "TERMINATED", "FAULTY", "REQUEST_RECEIVED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def size_in_gbs(self):
        """
        Gets the size_in_gbs of this VolumeBackup.
        The size of the volume, in GBs.


        :return: The size_in_gbs of this VolumeBackup.
        :rtype: int
        """
        return self._size_in_gbs

    @size_in_gbs.setter
    def size_in_gbs(self, size_in_gbs):
        """
        Sets the size_in_gbs of this VolumeBackup.
        The size of the volume, in GBs.


        :param size_in_gbs: The size_in_gbs of this VolumeBackup.
        :type: int
        """
        self._size_in_gbs = size_in_gbs

    @property
    def size_in_mbs(self):
        """
        Gets the size_in_mbs of this VolumeBackup.
        The size of the volume in MBs. The value must be a multiple of 1024.
        This field is deprecated. Please use sizeInGBs.


        :return: The size_in_mbs of this VolumeBackup.
        :rtype: int
        """
        return self._size_in_mbs

    @size_in_mbs.setter
    def size_in_mbs(self, size_in_mbs):
        """
        Sets the size_in_mbs of this VolumeBackup.
        The size of the volume in MBs. The value must be a multiple of 1024.
        This field is deprecated. Please use sizeInGBs.


        :param size_in_mbs: The size_in_mbs of this VolumeBackup.
        :type: int
        """
        self._size_in_mbs = size_in_mbs

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this VolumeBackup.
        The date and time the volume backup was created. This is the time the actual point-in-time image
        of the volume data was taken. Format defined by RFC3339.


        :return: The time_created of this VolumeBackup.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this VolumeBackup.
        The date and time the volume backup was created. This is the time the actual point-in-time image
        of the volume data was taken. Format defined by RFC3339.


        :param time_created: The time_created of this VolumeBackup.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_request_received(self):
        """
        Gets the time_request_received of this VolumeBackup.
        The date and time the request to create the volume backup was received. Format defined by RFC3339.


        :return: The time_request_received of this VolumeBackup.
        :rtype: datetime
        """
        return self._time_request_received

    @time_request_received.setter
    def time_request_received(self, time_request_received):
        """
        Sets the time_request_received of this VolumeBackup.
        The date and time the request to create the volume backup was received. Format defined by RFC3339.


        :param time_request_received: The time_request_received of this VolumeBackup.
        :type: datetime
        """
        self._time_request_received = time_request_received

    @property
    def unique_size_in_gbs(self):
        """
        Gets the unique_size_in_gbs of this VolumeBackup.
        The size used by the backup, in GBs. It is typically smaller than sizeInGBs, depending on the space
        consumed on the volume and whether the backup is full or incremental.


        :return: The unique_size_in_gbs of this VolumeBackup.
        :rtype: int
        """
        return self._unique_size_in_gbs

    @unique_size_in_gbs.setter
    def unique_size_in_gbs(self, unique_size_in_gbs):
        """
        Sets the unique_size_in_gbs of this VolumeBackup.
        The size used by the backup, in GBs. It is typically smaller than sizeInGBs, depending on the space
        consumed on the volume and whether the backup is full or incremental.


        :param unique_size_in_gbs: The unique_size_in_gbs of this VolumeBackup.
        :type: int
        """
        self._unique_size_in_gbs = unique_size_in_gbs

    @property
    def unique_size_in_mbs(self):
        """
        Gets the unique_size_in_mbs of this VolumeBackup.
        The size used by the backup, in MBs. It is typically smaller than sizeInMBs, depending on the space
        consumed on the volume and whether the backup is full or incremental.
        This field is deprecated. Please use uniqueSizeInGBs.


        :return: The unique_size_in_mbs of this VolumeBackup.
        :rtype: int
        """
        return self._unique_size_in_mbs

    @unique_size_in_mbs.setter
    def unique_size_in_mbs(self, unique_size_in_mbs):
        """
        Sets the unique_size_in_mbs of this VolumeBackup.
        The size used by the backup, in MBs. It is typically smaller than sizeInMBs, depending on the space
        consumed on the volume and whether the backup is full or incremental.
        This field is deprecated. Please use uniqueSizeInGBs.


        :param unique_size_in_mbs: The unique_size_in_mbs of this VolumeBackup.
        :type: int
        """
        self._unique_size_in_mbs = unique_size_in_mbs

    @property
    def volume_id(self):
        """
        Gets the volume_id of this VolumeBackup.
        The OCID of the volume.


        :return: The volume_id of this VolumeBackup.
        :rtype: str
        """
        return self._volume_id

    @volume_id.setter
    def volume_id(self, volume_id):
        """
        Sets the volume_id of this VolumeBackup.
        The OCID of the volume.


        :param volume_id: The volume_id of this VolumeBackup.
        :type: str
        """
        self._volume_id = volume_id

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
