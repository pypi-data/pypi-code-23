"""
Patch and improve boto and kombu
"""
from swarm_bus.settings import settings


def fix_libs():
    """
    Mock patching kombu 4.0.2 and boto 2.45
    """
    import boto.sqs.connection
    import kombu.transport.SQS

    from boto.sqs.queue import Queue as BotoQueue
    from kombu.five import Empty

    def drain_events_patched(self, timeout=None, **kwargs):
        """
        Override drain_events, by adding **kwargs argument.
        """
        if not self._consumers or not self.qos.can_consume():
            raise Empty()
        self._poll(self.cycle, self.connection._deliver, timeout=timeout)

    def create_queue_patched(self, queue_name, visibility_timeout=None):
        """
        Override create_queue, by configuring more parameters
        """
        queues = settings.amqp['QUEUES']
        base_queue_name = queue_name.split('-')[-1]
        params = {'QueueName': queue_name}
        params['Attribute.1.Name'] = 'VisibilityTimeout'
        params['Attribute.1.Value'] = queues[base_queue_name].get(
            'visibility', 1800)
        params['Attribute.2.Name'] = 'ReceiveMessageWaitTimeSeconds'
        params['Attribute.2.Value'] = queues[base_queue_name].get(
            'wait', 10)
        return self.get_object('CreateQueue', params, BotoQueue)

    boto.sqs.connection.SQSConnection.create_queue = create_queue_patched
    kombu.transport.SQS.Channel.drain_events = drain_events_patched
