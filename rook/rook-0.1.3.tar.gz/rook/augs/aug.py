"""This module implements the Aug class."""

from rook.lib.logger import logger

from rook.lib.user_warnings import UserWarnings

from rook.lib.processor.error import Error

from rook.exceptions import ToolException


class Aug(object):
    """The Aug class is the skeleton that holds together all the components that define a modification to the application.

    This class brings together the following elements:
    - location - specifies when to run the modification.
    - extractor - specifies attributes to extract from the application's state before evaluating the modification.
    - condition - specifies an optional filter as to when to run the modification.
    - action - specifies the modification to preform.
    """

    def __init__(self, aug_id, location, extractor, condition, action, output):
        """Build an Aug object from the individual elements."""
        self.aug_id = aug_id
        self._location = location
        self._extractor = extractor
        self._condition = condition
        self._action = action
        self._output = output

        self._status = None

    def add_aug(self, trigger_services):
        """Use the location to add the Aug to the relevant trigger service."""
        try:
            self._location.add_aug(trigger_services, self._output, self)
        except Exception as exc:
            message = "Exception when adding aug"
            logger.exception(message)
            self.set_error(Error(exc=exc, message=message))

    def execute(self, frame, extracted):
        """Called by the trigger service to run the extractor, condition and action."""
        try:
            with UserWarnings(self):
                logger.debug("Executing aug-\t%s", self.aug_id)
                if self._extractor:
                    self._extractor.execute(frame, extracted)

                if not self._condition or self._condition.evalute(frame, extracted):
                    self._action.execute(self.aug_id, frame, extracted, self._output)
        # Don't stop test exceptions from propagating
        except AssertionError:
            raise
        # Catch and silence everything else
        except Exception as exc:
            message = "Exception while processing Aug"
            logger.exception(message)
            self.send_warning(Error(exc=exc, message=message))

    def set_active(self):
        self._send_rule_status("Active")

    def set_pending(self):
        self._send_rule_status("Pending")

    def set_removed(self):
        self._send_rule_status("Deleted")

    def set_error(self, error):
        self._send_rule_status("Error", error)

    def set_unknown(self, error):
        self._send_rule_status("Unknown", error)

    def send_warning(self, error):
        self._output.send_warning(self.aug_id, error)

    def _send_rule_status(self, status, error=None):
        if self._status == status:
            return

        logger.info("Updating rule status for %s to %s", self.aug_id, status)

        self._status = status
        self._output.send_rule_status(self.aug_id, status, error)
