import datetime
import simplejson as json
import time
import uuid


class QueueListener():
    config = {}

    def __init__(self, config):
        self.config = config


    def _receive(self, queue_name):
        response = self.config['sqs'].receive_message(
            QueueUrl=queue_name,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=30,
            WaitTimeSeconds=20
        )

        if 'Messages' in response:
            raw_message = response['Messages'][0]
            message = Message(self.config, raw_message, queue_name)
            return message
        else:
            return None


class Message():
    _config = {}
    _event = False
    _raw_message = None
    _queue = None
    _payload = None
    _body = None

    def __init__(self, config=None, raw_message=None, queue=None, event=True):
        self._config = config
        self._raw_message = raw_message
        self._queue = queue
        self._event = event
        self._init()

    def _init(self):
        if self._event:
            self._payload = json.loads(self._raw_message['Body'])
            self._body = json.loads(self._payload['Message'])
        else:
            self._payload = self._raw_message
            self._body = self._payload

    def _is_json(self, string):
        try:
            json.loads(string)
        except ValueError as e:
            return False
        return True

    def _receipt_handle(self):
        return self._raw_message['ReceiptHandle']

    def attributes(self):
        return self._payload['MessageAttributes']

    def body(self):
        return self._body

    def id(self):
        return self._body['id']

    def ref(self):
        return self._body['ref_id']


    def action(self):
        return self._body['action']

    def strategy(self):
        return self._body['data']['strategy']

    def data(self):
        return self._body['data']

    def source(self):
        return self._body['source_id']

    def is_valid(self):
        return False if self._payload is None else True

    def delete(self):
        self._config['sqs'].delete_message(
            QueueUrl=self._queue,
            ReceiptHandle=self._receipt_handle()
        )

    def payload(self):
        return self._payload

    def payloads(self):
        return json.dumps(self._payload, indent=4)


class MessageProducer():
    config = {}

    def __init__(self, config):
        pass

    def notify(self, original_message, category, action, data, delay=False):
        timestamp = int(round(time.time() * 1000))
        payload = {
            'id': str(uuid.uuid4()),
            'ref_id': original_message.id(),
            'source_id': original_message.source(),
            'date': str(datetime.datetime.fromtimestamp(timestamp / 1000)),
            'date_timestamp': timestamp,
            'action': action,
            'data': data
        }

        delay_data = {'DataType': 'String', 'StringValue': str(delay).lower()}
        message_attrs = {'action': {'DataType': 'String', 'StringValue': action}, 'category': {'DataType': 'String', 'StringValue': category}}
        if delay:
            message_attrs['delay'] = delay_data

        response = self.config['sns'].publish(
            TopicArn=self.config['notification_endpoint'],
            Message=json.dumps(payload),
            MessageAttributes=message_attrs
        )
