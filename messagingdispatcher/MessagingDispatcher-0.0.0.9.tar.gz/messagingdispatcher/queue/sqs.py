import boto3

class Sqs(object):
    def __init__(self, queue_name):
        self._sqs_resource = boto3.client('sqs')
        self._queue_url = self.get_queue_url(queue_name=queue_name)

    def get_queue_url(self, queue_name):
        response = self._sqs_resource.get_queue_url(QueueName=queue_name)
        return response['QueueUrl']

    def send_message(self, message_body, delay_seconds=0):
        return self._sqs_resource.send_message(QueueUrl=self._queue_url,
                                               MessageBody=message_body,
                                               DelaySeconds=delay_seconds)

    def get_messages(self,
                     attribute_names=['All'],
                     max_number_of_messages=10,
                     visibility_timeout=60,
                     wait_time_seconds=5):
        return self._sqs_resource.receive_message(QueueUrl=self._queue_url,
                                                  AttributeNames=attribute_names,
                                                  MaxNumberOfMessages=max_number_of_messages,
                                                  VisibilityTimeout=visibility_timeout,
                                                  WaitTimeSeconds=wait_time_seconds)

    def delete_messages(self, receipt_handles):
        return self._sqs_resource.delete_message_batch(
            QueueUrl=self._queue_url,
            Entries=receipt_handles
        )
