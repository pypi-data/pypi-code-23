import time
import threading
from typing import NamedTuple

from elife_bus_sdk.queues import SQSMessageQueue


def test_can_get_queue(sqs_message_queue: SQSMessageQueue):
    assert sqs_message_queue.queue


def test_can_send_message(sqs_message: NamedTuple, sqs_message_queue: SQSMessageQueue):
    assert sqs_message_queue.enqueue(sqs_message)


def test_can_call_dequeue(sqs_message_queue: SQSMessageQueue):
    message = sqs_message_queue.dequeue()[0]
    assert message == {
        'body': 'body',
        'md5_of_body': 'md5 body',
        'message_id': '0000000',
        'queue_url': 'some url',
        'receipt_handle': '111111',
        'type': 'base_msg'
    }


def test_can_check_polling_state(sqs_message_queue: SQSMessageQueue):
    assert not sqs_message_queue.is_polling()


def test_can_start_and_polling(sqs_message_queue: SQSMessageQueue):
    def poll_wrapper():
        try:
            while True:
                next(sqs_message_queue.poll())
        except StopIteration:
            pass

    poll_thread = threading.Thread(target=poll_wrapper)
    poll_thread.start()

    assert sqs_message_queue.is_polling()

    time.sleep(1)
    sqs_message_queue.stop_polling()
    poll_thread.join()

    assert not sqs_message_queue.is_polling()
