from time import sleep

import boto3
import os

from logger import create_logger

logger = create_logger(__name__)


def get_queue():
    sqs = boto3.resource('sqs', region_name=os.environ.get('aws_region'))
    queue = sqs.get_queue_by_name(QueueName=os.environ.get('queue_name'))
    return queue


def delete_message_client(queue_url, receipt_handle):
    sqs = boto3.client('sqs', region_name=os.environ.get('aws_region'))
    response = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        logger.error('Failed to delete message')


def delete_message_resource(receipt_handle):
    message_id = '0'  # TODO change it if we track deletion logs
    queue = get_queue()
    response = queue.delete_messages(Entries=[{'Id': message_id, 'ReceiptHandle': receipt_handle}])
    if 'Failed' in response:
        logger.error('Failed to delete message')


def get_messages(queue, num_messages=10, sleep_time=10):
    while True:
        messages = queue.receive_messages(MaxNumberOfMessages=num_messages)
        if messages:
            return messages
        sleep(sleep_time)
