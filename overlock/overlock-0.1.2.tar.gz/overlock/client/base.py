from abc import abstractmethod


class BaseClient(object):
    """Base class for a client that interacts with the overlock agent somehow
    """

    @abstractmethod
    def update_state(self, new_state):
        """Update existing state with new state

        Args:
            new_state (dict): Dictionary of new state - should be of the form:

        Example:

            .. code-block:: python

                logger.update_state({
                    "a": 123,
                    "b": 456,
                })
        """

    @abstractmethod
    def update_metadata(self, new_metadata):
        """Update metadata with new metadata

        Args:
            new_metadata (dict): Dictionary of new metadata

        Example:

            .. code-block:: python

                logger.update_metadata({
                    "a": 123,
                    "b": 456,
                })
        """

    @abstractmethod
    def lifecycle_event(self, key_type, comment):
        """Update the lifecycle of the program

        Args:
            key_type (str): Type of key
            comment (str): Value of key

        Example:

            .. code-block:: python

                logger.lifecycle_event("readings", "started")
        """
