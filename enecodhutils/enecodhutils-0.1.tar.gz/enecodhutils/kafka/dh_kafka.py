import json
import hashlib
import logging
from datetime import datetime
from pykafka import KafkaClient


def produce_msg_to_kafka(bootstrap_server, topic, message, hash_columns=None, partition_col=False):
    """
    Produce the input message to the given kafka topic
    :param message: JSON array containing the messages
    :type message: JSON String
    :param bootstrap_server: The location of the kafka bootstrap server
    :type bootstrap_server: String
    :param topic: The topic to which the message is produced
    :type topic: String
    :param hash_columns: The list of columns to use to generate primary key. Default 'None' will result in all columns.
    :type hash_columns: List
    :param partition_col: Boolean to add a partition_col value or not.
    :type partition_col: Boolean
    """
    logging.info('DH_Utils: Producing message to Kafka')
    # Setup the kafka producer
    client = KafkaClient(bootstrap_server)
    topic = client.topics[topic.encode()]
    producer = topic.get_producer(sync=False, min_queued_messages=1)
    records = json.loads(message)
    for record in records:
        record.update({'uid': generate_hash(record, hash_columns),
                       'processed_time': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")})
        if partition_col:
            record.update({'partition_col': generate_partition_col(record['datetime'])})
        producer.produce(json.dumps(record).encode())
    logging.info('DH_Utils: Finished producing message to Kafka')
    producer.stop()


def generate_partition_col(record_time):
    """
    Generate the partition column value based on the time.
    :param record_time: The datetime value for the record.
    :type record_time: String
    :return: partition_col: Integer
    """
    partition_col = int(datetime.strptime(record_time,
                                          "%Y-%m-%d %H:%M:%S").strftime('%m%d%H'))
    return partition_col


def generate_hash(record, hash_columns):
    """
    Generate a hash object for the record to maintain uniqueness.
    :param record: The json record for whose columns the hash has to be generated.
    :type record: Dictionary
    :param hash_columns:The columns on which the hash has to be generated.
    :type hash_columns:  List[Strings]
    :return: hash_object: String
    """
    hash_string = ''
    if hash_columns:
        for col in hash_columns:
            hash_string = hash_string + str(record[col])
    else:
        hash_string = hash_string + json.dumps(record)
    hash_object = hashlib.md5(hash_string.encode()).hexdigest()
    return hash_object
