import json
import six

from base10.base import Dialect, Metric
from base10.exceptions import DialectError


class JSONDialect(Dialect):
    """
    {
        name: 'cpu_usage',
        fields: {
            user: 0.2,
            free: 0.75
        },
        metadata: {
            hostname: 'host-1'
        },
        timestamp: 1489478831
    }
    """

    def from_string(self, string):
        try:
            data = json.loads(string)

            name = data['name']
            fields = list(six.iterkeys(data['fields']))
            metadata = list(six.iterkeys(data['metadata']))
            timestamp = data['timestamp']

            kwargs = {}
            kwargs.update(data['fields'])
            kwargs.update(data['metadata'])

            return Metric(
                name=name,
                fields=fields,
                metadata=metadata,
                time=timestamp,
                **kwargs
            )
        except ValueError as e:
            raise DialectError('Could not decode JSON', e)
        except KeyError as e:
            raise DialectError('Metric didn\'t contain all necessary fields', e)

    def to_string(self, metric):
        return json.dumps(
            {
                'name': metric.name,
                'fields':
                    {
                        k: v
                        for k, v in metric.values.items() if k in metric.fields
                    },
                'metadata':
                    {
                        k: v
                        for k, v in metric.values.items()
                        if k in metric.metadata
                    },
                'timestamp': metric.values['time']
            }
        )
