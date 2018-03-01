from kafka_communicator import KafkaCommunicator


def get_kafka_communicator(ip, port):
    return KafkaCommunicator(ip = ip, port = port)

def send_kafka_message(kafka_communicator, topic, data, is_str = True):
    
    if isinstance(kafka_communicator, KafkaCommunicator) == False:
        raise ValueError('The kafka_communicator passed in is not the right type')
    
    is_sent = kafka_communicator.send_message(topic = topic, data = data, is_str = is_str)
    return is_sent

def send_kafka_test_message(ip, port, message):
    is_sent = KafkaCommunicator.send_test_message(ip = ip, port = port, data = message)
    print('test message response', is_sent)
    
    return is_sent


if __name__ == '__main__':
    ip = None 
    port = 9092
    
    kafka_communicator = KafkaCommunicator(ip = ip, port = port)
    is_sent = send_kafka_message(kafka_communicator = kafka_communicator, topic = 'weather', data = 'this is test data!!')
    is_sent = send_kafka_message(kafka_communicator = kafka_communicator, topic = 'weather', data = 'asdfasd!!')
    print(is_sent)