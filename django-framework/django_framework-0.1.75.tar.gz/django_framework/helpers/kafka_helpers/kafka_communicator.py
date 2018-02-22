import json

from kafka import SimpleProducer, KafkaClient, KafkaProducer



class KafkaCommunicator():
    
    def __init__(self, ip, port, kafka_producer = None):

        self.ip = ip
        self.port = port
        
        self._kafka_producer = kafka_producer
        
    def send_message(self, topic, data, is_str = True):
        # data should be a string!!
        
        if is_str != True:
            is_str = str.encode(json.dumps(self.data))

        is_sent = False
        try:
            self.kafka_producer.send_messages(topic, data)
            is_sent = True
            
        except ValueError as e:
            print('There was an issue probably with the message')
            print(e)
            
        except Exception as e:
            print('There was an issue sending the message to kafka')
            print(e)
            self.close_connection()
        
        return is_sent
    
    
    def close_connection(self):
        
        # close the connection if it isnt blank!
        if self.kafka_producer != None:
            self.kafka_producer.close()
        
        # reset the kafka_producer
        self._kafka_producer = None
            
    @property
    def kafka_producer(self):
        if self._kafka_producer == None:
            self._kafka_producer = self.create_kafka_producer(ip = self.ip, port = self.port)
        return self._kafka_producer
    
    @classmethod
    def create_kafka_producer(cls, ip, port):
        ip = cls.create_ip(ip = ip, port = port)
        kafka = KafkaClient([ip])
        producer = SimpleProducer(kafka,
                          req_acks=SimpleProducer.ACK_AFTER_LOCAL_WRITE,
                          ack_timeout=500,
                         )
        
        return producer
    
    
    @classmethod
    def send_test_message(cls, ip, port, data):
        ip = cls.create_ip(ip = ip, port = port)
        
        if data == None:
            data = 'This is a test message!'
        elif type(data) != str:
            raise ValueError('inputted test data needs to be a str!')
        
        producer = KafkaProducer(bootstrap_servers=[ip], 
                                 acks =1, 
                                 linger_ms=0, 
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        
        # Asynchronous by default
        response = producer.send('TutorialTopic', data)
        return response
    
    @classmethod
    def create_ip(self, ip, port):
        return '{ip}:{port}'.format(ip = ip, port = port)
    


    


