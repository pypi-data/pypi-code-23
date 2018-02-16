import logging
import time
import threading

import netuitive

from .elements import Elements
from .statsd import parse_message

logger = logging.getLogger(__name__)


class Poster(threading.Thread):

    """
    Thread for posting the collected data to Netuitive's API
    """

    def __init__(self, config, element, version='develop'):
        logger.debug('Poster')
        threading.Thread.__init__(self)
        self.setName('PosterThread')
        self.lock = threading.Lock()
        self.config = config
        self.runner = threading.Event()
        self.sample_count = float(0)
        self.packet_count = float(0)
        self.event_count = float(0)
        self.metric_prefix = self.config['prefix']
        self.stats_prefix = self.metric_prefix + '.netuitive-statsd'
        self.no_internal_metrics = self.config['no_internal_metrics']

        self.flush_time = 0
        logger.debug('Messages will be sent to ' + self.config['url'])

        self.api = netuitive.Client(self.config['url'],
                                    self.config['api_key'],
                                    agent='Netuitive-Statsd/' + str(version))

        self.interval = int(self.config['interval'])
        self.hostname = config['hostname']
        self.events = []
        self.elements = Elements(self.hostname, element)

        self.flush_error_count = 0
        self.flush_error_max = max(self.interval * 15, 900)

    def stop(self):
        logger.debug("Poster Shutting down")
        self.runner.set()

    def run(self):
        """
        start the loop
        """

        while not self.runner.is_set():
            logger.debug('Waiting {0} seconds'.format(self.interval))
            self.runner.wait(self.interval)
            logger.debug('Flushing')
            if self.flush():
                logger.debug('Flush sucessful')

            else:
                logger.error('Error during flush')

    def flush(self):
        """
        send the data to the Netuitive API and remove the local data
        """

        try:
            with self.lock:
                if self.flush_error_count >= self.flush_error_max:
                    logger.error(
                        'failed to post for at least {0} seconds. '.format(
                            self.flush_error_max) +
                        'dropping data to prevent memory starvation.'
                    )

                    self.elements.delete_all()
                    return(False)

                timestamp = int(time.time())

                if self.no_internal_metrics is False:
                    # add some of our internal metric samples
                    self.elements.add(self.stats_prefix +
                                      '.packets_received.count',
                                      timestamp,
                                      self.packet_count,
                                      'c',
                                      elementId=self.hostname)

                    self.elements.add(self.stats_prefix +
                                      '.samples_received.count',
                                      timestamp,
                                      self.sample_count,
                                      'c',
                                      elementId=self.hostname)

                    self.elements.add(self.stats_prefix +
                                      '.event_received.count',
                                      timestamp,
                                      self.event_count,
                                      'c',
                                      elementId=self.hostname)

                    logger.debug('Sample count: {0}'.format(self.sample_count))
                    logger.debug('Packet count: {0}'.format(self.packet_count))
                    logger.debug('Event count: {0}'.format(self.event_count))

                logger.debug(
                    'Flushing {0} samples and '
                    '{1} events total'.format(self.sample_count,
                                              self.event_count))

                ec = 0
                sc = 0

                for ename in self.elements.elements:
                    e = self.elements.elements[ename]
                    e.prepare()
                    element = e.element
                    sample_count = len(element.samples)
                    ec += 1
                    sc += sample_count

                    logger.debug('{0} has {1} samples'.format(ename,
                                                              sample_count))

                    for s in element.samples:
                        logger.debug('elementId: {0} metricId: '
                                     '{1} value: {2} timestamp: {3}'.format(
                                         ename,
                                         s.metricId,
                                         s.val,
                                         str(s.timestamp)))

                    if sc > 0:
                        logger.debug(
                            'sending {0} samples for for {1}'.format(sc,
                                                                     ename))

                        # do the post
                        if self.api.post(element):
                            self.elements.clear_samples(ename)
                            logger.debug(
                                "Successfully sent {0} elements with "
                                "{1} samples total".format(ec, sc))

                            elapsed = int(time.time()) - self.flush_time
                            if elapsed > 900 or self.flush_time == 0:
                                self.flush_time = int(time.time())
                                logging.info('Data posted Successfully. '
                                             'Next log message in 15 minutes.')

                        else:
                            logger.error(
                                "Failed to send {0} elements with "
                                "{1} samples total".format(ec, sc))

                logger.debug(
                    'Flushing {0} events'.format(len(self.events)))

                for event in self.events:

                    if self.api.post_event(event):
                        logger.debug(
                            "Successfully sent event "
                            "titled {0}".format(event.title))

                    else:
                        logger.warning(
                            "Failed to send {0} event "
                            "titled {0}".format(event.title))

                # reset
                self.sample_count = 0
                self.packet_count = 0
                self.event_count = 0
                self.events = []
                self.elements.delete_all()
                return(True)

        except Exception as e:
            logger.error(e, exc_info=True)

        self.flush_error_count += self.interval
        return(False)

    def submit(self, message, ts):
        """
        process incoming messages
        """

        timestamp = int(ts)

        try:

            self.packet_count += 1

            messages = parse_message(message)

            if messages is not None:
                self.sample_count += float(messages['counts']['messages'])
                self.event_count += float(messages['counts']['events'])

                # process an event message
                if len(messages['events']) > 0:

                    for e in messages['events']:

                        title = e['title']
                        text = e['text']
                        tgs = e['tags']
                        tags = []

                        for t in tgs:
                            for k, v in t.items():
                                tags.append((k, v))

                        if e['hostname'] is None:
                            eid = self.hostname
                        else:
                            eid = e['hostname']

                        lvl = 'INFO'
                        if e['priority'] is not None:
                            tags.append(('priority', e['priority']))

                            if e['priority'].upper() == "CRITICAL":
                                lvl = "CRITICAL"

                            if e['priority'].upper() == "WARNING":
                                lvl = "WARNING"

                        if e['date_happened'] is not None:
                            tags.append(
                                ('date_happened', e['date_happened']))

                        if e['aggregation_key'] is not None:
                            tags.append(
                                ('aggregation_key', e['aggregation_key']))

                        if e['source_type_name'] is not None:
                            tags.append(
                                ('source_type_name', e['source_type_name']))

                        if e['alert_type'] is not None:
                            tags.append(('alert_type', e['alert_type']))

                        with self.lock:
                            self.events.append(
                                netuitive.Event(eid,
                                                'INFO',
                                                title,
                                                text,
                                                lvl,
                                                tags,
                                                timestamp,
                                                'netuitive-statsd'))

                # process a metric/sample message
                if len(messages['metrics']) > 0:
                    for m in messages['metrics']:
                        with self.lock:
                            self.elements.add(
                                self.metric_prefix + '.' + m['name'],
                                timestamp,
                                m['value'],
                                m['type'],
                                m['sign'],
                                m['rate'],
                                m['tags'],
                                m['hostname']
                            )

        except Exception as e:
            logger.error(
                'Invalid Packet Format: "' + str(message).rstrip() + '"')
            logger.error(e, exc_info=True)
