import logging
import msgpack
import traceback
import sys

try:
    import confluent_kafka
    from confluent_kafka import KafkaError, KafkaException
except:
    pass

logger = logging.getLogger()
api_version_request = True


def read_notification_from_ceilometer_over_kafka(conf, topic, pid, callback):
    default_conf = {'group.id': pid,
            'session.timeout.ms': 6000,
            'enable.auto.commit': False,
            'log_level':2,
            'default.topic.config': {
                 'auto.offset.reset': 'earliest'
            }}
    conf.update(default_conf)
    consumer = confluent_kafka.Consumer(**conf)
    consumer.subscribe([topic])
    try:
        while True:
            msg = consumer.poll(timeout=10)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    raise KafkaException(msg.error())
            else:
                data = None
                if msg.value():
                    data = msgpack.loads(msg.value(), encoding='utf-8')
                    if data:
                        t = msg.topic()
                        if t and callback:
                            try:
                                callback(data)
                                logger.info("{} << {}".format(t, data))
                            except Exception as e:
                                logger.error(e)
                                traceback.print_exc()
                            consumer.commit(msg, async=True)
    except KeyboardInterrupt:
        print('%% Aborted by user\n')
    consumer.close()


def send_message(conf, topic, message):

        default_conf = {'api.version.request': api_version_request,
                        'default.topic.config': {'produce.offset.report': True}
                        }
        conf.update(default_conf)
        p = confluent_kafka.Producer(**conf)

        try:
            p.produce(topic, value=msgpack.dumps(message, use_bin_type=True))
            logger.info("{} >> {}".format(topic, message))
            p.poll(0)
        except BufferError as e:
            print('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                            len(p))
        p.flush()

