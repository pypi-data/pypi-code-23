"""Test the Django DataDog integration.
"""
try:
    from unittest import TestCase, main, mock
except ImportError:
    import mock
    from unittest import TestCase, main

from django.conf import settings
from django.test import override_settings

from django_datadog.compat import create_event, create_gauge


NOT_CONFIGURED = {'DATADOG': {'ENABLED': False}}
CONFIGURED = {'DATADOG': {'ENABLED': True,
                          'API_KEY': 'test',
                          'APP_KEY': 'test'},
              'STATSD_HOST': 'localhost',
              'STATSD_PORT': '12334'}

settings.configure()


@mock.patch('django_datadog.compat.api')
class EventTestCase(TestCase):
    """Test DataDog events.
    """

    @override_settings(**NOT_CONFIGURED)
    def test_not_configured(self, api):
        """Do not send events if not configured.
        """
        create_event('test_event', fmt_text='Extended text')
        self.assertFalse(api.Event.create.called)

    @override_settings(**CONFIGURED)
    def test_configured(self, api):
        """Send an event if configured.
        """
        create_event('test_event', fmt_text='Extended text')
        self.assertTrue(api.Event.create.called)

        api.Event.create.assert_called_with(alert_level='info',
                                            priority='low',
                                            text='Extended text',
                                            title='test_event')

    @override_settings(**CONFIGURED)
    def test_format_text(self, api):
        """Send formatted text.
        """
        create_event('test_event', fmt_text='Extended text: %s',
                     text_args=('Value',))
        self.assertTrue(api.Event.create.called)

        api.Event.create.assert_called_with(alert_level='info',
                                            priority='low',
                                            text='Extended text: Value',
                                            title='test_event')


@mock.patch('django_datadog.compat.statsd')
class GaugeTestCase(TestCase):
    """Test DataDog Gauges.
    """

    @override_settings(**NOT_CONFIGURED)
    def test_not_configured(self, statsd):
        """Do not send events if not configured.
        """
        create_gauge('some_gauge', value=10)
        self.assertFalse(statsd.gauge.called)

    @override_settings(**CONFIGURED)
    def test_configured(self, statsd):
        """Send an event if configured.
        """
        create_gauge('some_gauge', value=10)
        self.assertTrue(statsd.gauge.called)

        statsd.gauge.assert_called_with(metric='some_gauge', value=10,
                                        tags=None, sample_rate=1)


if __name__ == '__main__':
    main()
