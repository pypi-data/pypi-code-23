import json


class Message(object):
    def __init__(self, text=None, attachment=None, quick_replies=None):
        if not text and not attachment:
            raise ValueError('The text or attachment value are required.')

        self.text = text
        self.attachment = attachment
        self.quick_replies = quick_replies

    def get_data(self):
        data = {}

        if self.text:
            data['text'] = self.text

        if self.attachment:
            data['attachment'] = self.attachment.get_data()

        if self.quick_replies:
            data['quick_replies'] = self.quick_replies.get_data()

        return data


class Recipient(object):
    def __init__(self, recipient_id=None, phone_number=None):
        if not recipient_id and not phone_number:
            raise ValueError('The recipient id or phone number are required.')
        self.recipient_id = recipient_id
        self.phone_number = phone_number

    def get_data(self):
        if self.recipient_id:
            return {'id': self.recipient_id}
        return {'phone_number': self.phone_number}


class RequestDataFormat(object):
    def __init__(self, recipient=None, message=None, sender_action=None, notification_type=None, message_type=None):
        if not recipient:
            raise ValueError('The recipient is required.')

        if not message and not sender_action:
            raise ValueError('The message or sender action value are required.')

        if not sender_action and not message_type:
            raise ValueError('The message type value are required.')

        self.recipient = recipient
        self.message = message
        self.sender_action = sender_action
        self.notification_type = notification_type
        self.message_type = message_type

    def get_data(self):
        data = {}

        if self.recipient:
            data['recipient'] = self.recipient.get_data()

        if self.message and type(self.message) is dict:
            data['message'] = self.message
        elif self.message:
            data['message'] = self.message.get_data()

        if self.sender_action:
            data['sender_action'] = self.sender_action

        if self.notification_type:
            data['notification_type'] = self.notification_type

        if self.message_type:
            data['message_type'] = self.message_type

        return data

    def serialise(self):
        return json.dumps(self.get_data())
