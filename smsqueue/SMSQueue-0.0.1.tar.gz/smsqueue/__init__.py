import requests

from http import HTTPStatus


class SMSQueue(object):
    """
    The main class handling queueing SMS messages.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://app.smsqueue.io'

    def get_all_sms(self):
        """
        Handles retrieving a list of all SMS under an account.

        :rtype: list[QueuedSMS]
        :returns: A list of all SMS found for the provided API Key.
        """
        r = requests.get(
            '{0}/api/messages/sms'.format(self.base_url),
            headers={'Authorization': 'Basic {0}'.format(self.api_key)}
        )
        if r.status_code != HTTPStatus.OK:
            raise _smsqueue_exception_factory(r)

        return r.json()

    def get_sms(self, public_id):
        """
        Handles retrieving a specific SMS by it's public ID.

        :param str public_id: The ID of the SMS we want to retrieve.
        :rtype: QueuedSMS
        :raises: SMSQueueNotFound
        :returns: The specified SMS queried.
        """
        r = requests.get(
            '{0}/api/messages/sms/{1}'.format(self.base_url, public_id),
            headers={'Authorization': 'Basic {0}'.format(self.api_key)}
        )
        if r.status_code != HTTPStatus.OK:
            raise _smsqueue_exception_factory(r)

        return r.json()

    def enqueue_sms(self, sms_message):
        """
        Handles queueing a new SMS.

        :param SMSMessage sms_message: The SMS we're wanting to queue.
        :rtype: QueuedSMS
        :returns: The newly created SMS.
        """
        print(sms_message.to_dictionary())
        r = requests.post(
            '{0}/api/messages/sms'.format(self.base_url),
            json=sms_message.to_dictionary(),
            headers={
                'Authorization': 'Basic {0}'.format(self.api_key),
                'Content-Type': 'application/json'
            },
        )
        if r.status_code != HTTPStatus.OK:
            raise _smsqueue_exception_factory(r)

        return r.json()

    def delete_sms(self, public_id):
        """
        Handles deleting a SMS. NOTE: This only works for messages in the "QUEUED" state.

        :param str public_id: The public ID of the message we're wanting to delete.
        """
        r = requests.delete(
            '{0}/api/messages/sms/{1}'.format(self.base_url, public_id),
            headers={'Authorization': 'Basic {0}'.format(self.api_key)}
        )
        if r.status_code != HTTPStatus.OK:
            raise _smsqueue_exception_factory(r)

        return r.json()


class SMSMessage(object):
    """
    The model used for queueing/POSTing new messages.
    """

    def __init__(self, phone_number, message, remind_at):
        """
        :param str phone_number: The phone number we want to send a message to
        :param str message: The message we want sent.
        :param str remind_at: A string representation of ISO8601 datetime.
        """
        self.phone_number = phone_number
        self.message = message
        self.remind_at = remind_at

    def to_dictionary(self):
        """
        Handles converting the data type to a map.
        """
        return {
            'phone_number': self.phone_number,
            'message': self.message,
            'remind_at': self.remind_at
        }


class QueuedSMS(object):
    """
    The model stored in our system. Holds all information necessary to inspect queued SMS.
    """

    def __init__(self, public_id, state, phone_number, message, remind_at):
        """
        :param str public_id:
        """
        self.public_id = public_id
        self.state = state
        self.phone_number = phone_number
        self.message = message
        self.remind_at = remind_at


def _smsqueue_exception_factory(response):
    """
    Handles creating exception types based on their HTTP status code.
    """
    if response.status_code == HTTPStatus.BAD_REQUEST:
        return SMSQueueBadRequest(response)
    elif response.status_code == HTTPStatus.UNAUTHORIZED:
        return SMSQueueUnauthorized(response)
    elif response.status_code == HTTPStatus.FORBIDDEN:
        return SMSQueueForbidden(response)
    elif response.status_code == HTTPStatus.NOT_FOUND:
        return SMSQueueNotFound(response)
    elif response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        return SMSQueueUnprocessable(response)
    else:
        raise RuntimeError('Invalid response from remote server {0} with code {1}'.format(response.text, response.status_code))



class SMSQueueBaseException(BaseException):
    """
    The base model for exceptions in our system.
    """
    __abstract__ = True

    def __init__(self, response):
        self.error_message = response.text
        self.status_code = response.status_code
        self.response = response


class SMSQueueBadRequest(SMSQueueBaseException):
    pass


class SMSQueueUnauthorized(SMSQueueBaseException):
    pass


class SMSQueueForbidden(SMSQueueBaseException):
    pass


class SMSQueueNotFound(SMSQueueBaseException):
    pass


class SMSQueueUnprocessable(SMSQueueBaseException):
    pass
