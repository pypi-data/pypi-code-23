import logging
import re

logger = logging.getLogger(__name__)


def _sanitize(line):
    # try to make the metric names, graphite compatible
    line = re.sub(r"\s+", "_", line)
    line = re.sub(r"\/", "_", line)
    line = re.sub(r"^\.", "", line)
    line = re.sub(r"[^a-zA-Z_\-0-9\.]", "", line)

    return(line)


def parse_message(message):
    """
    parse a statsd message via string splitting and return the results
    """

    ret = {}
    ret['metrics'] = []
    ret['events'] = []

    sample_count = 0
    event_count = 0

    # split the messages on \n
    for msg in message.splitlines():
        try:
            parts = msg.split('|')

            if parts[0].startswith('_sc'):
                # it's an sc event message
                sample_count += 1
                event_count += 1
                date_happened = None
                hostname = None
                text = ''
                tags = []

                status = {'0': 'OK',
                          '1': 'WARNING',
                          '2': 'CRITICAL',
                          '3': 'UNKNOWN'}

                priority = status[str(parts[2])]

                title = parts[1] + ' - ' + priority

                for pt in parts:
                    if len(tags) == 0:
                        # look for tags
                        i = parts.index(pt)
                        for p in parts[i:]:
                            if p.startswith('#'):
                                tgs = p.replace('#', '')
                                for ts in tgs.split(','):
                                    t = ts.split(':')
                                    if len(t) == 2:
                                        tags.append({t[0]: t[1]})
                                    else:
                                        tags.append({t[0]: None})

                        # look for optional fields

                    if ':' in pt:
                        m = pt.split(':')
                        if m[0] == 'd':
                            date_happened = m[1]

                        elif m[0] == 'm':
                            text = m[1]

                        elif m[0] == 'h':
                            hostname = m[1]

                logger.debug(
                    'Message (sc event): ' + str((title,
                                                  text,
                                                  date_happened,
                                                  hostname,
                                                  None,
                                                  priority,
                                                  None,
                                                  None,
                                                  tags)))

                ret['events'].append({
                    'title': title,
                    'text': text,
                    'date_happened': date_happened,
                    'hostname': hostname,
                    'aggregation_key': None,
                    'priority': priority,
                    'source_type_name': None,
                    'alert_type': None,
                    'tags': tags})

            if parts[0].startswith('_e'):
                # it's an event message
                sample_count += 1
                event_count += 1
                date_happened = None
                hostname = None
                aggregation_key = None
                priority = None
                source_type_name = None
                alert_type = None
                tags = []

                title = parts[0].split(':')[1]
                text = parts[1]

                if len(parts) > 2:
                    # look for tags
                    for p in parts[2:]:
                        if p.startswith('#'):
                            tgs = p.replace('#', '')
                            for ts in tgs.split(','):
                                t = ts.split(':')
                                if len(t) == 2:
                                    tags.append({t[0]: t[1]})
                                else:
                                    tags.append({t[0]: None})

                        else:
                            m = p.split(':')

                            # look for optional fields
                            if m[0] == 'd':
                                date_happened = m[1]

                            elif m[0] == 'h':
                                hostname = m[1]

                            elif m[0] == 'k':
                                aggregation_key = m[1]

                            elif m[0] == 'p':
                                priority = m[1]

                            elif m[0] == 's':
                                source_type_name = m[1]

                            elif m[0] == 't':
                                alert_type = m[1]

                logger.debug(
                    'Message (event): ' + str((title,
                                               text,
                                               date_happened,
                                               hostname,
                                               aggregation_key,
                                               priority,
                                               source_type_name,
                                               alert_type,
                                               tags)))

                ret['events'].append({
                    'title': title,
                    'text': text,
                    'date_happened': date_happened,
                    'hostname': hostname,
                    'aggregation_key': aggregation_key,
                    'priority': priority,
                    'source_type_name': source_type_name,
                    'alert_type': alert_type,
                    'tags': tags})

            elif len(parts[0].split(':')) > 1:
                # it's a metric

                sample_count += 1
                rate = None
                sign = None
                hostname = None
                tags = []
                metric = _sanitize(parts[0].split(':')[0])
                v = parts[0].split(':')[1]
                mtype = parts[1]

                if mtype not in ['c', 'g', 'ms', 's', 'h']:
                    ret = {}
                    logger.error(
                        'Invalid Message Format: "' +
                        str(message).rstrip() + '"')
                    return(None)

                tags.append({'statsdType': mtype})

                # check for the value being signed or unsigned
                if v.startswith('-'):
                    sign = '-'
                    value = float(v[1:])

                elif v.startswith('+'):
                    sign = '+'
                    value = float(v[1:])

                else:
                    value = float(v)

                if len(parts) > 2:
                    # look for rate
                    if parts[2].startswith('@'):
                        rate = float(parts[2].replace('@', ''))

                    if parts[2].startswith('#'):
                        # look for tags
                        tgs = parts[2].replace('#', '')

                        for ts in tgs.split(','):
                            t = ts.split(':')
                            if len(t) == 2:
                                tags.append({t[0]: t[1]})
                                if t[0] == 'h':
                                    hostname = t[1]
                            else:
                                tags.append({t[0]: None})

                if len(parts) > 3:
                    # look for tags again
                    if parts[3].startswith('#'):
                        tgs = parts[3].replace('#', '')

                        for ts in tgs.split(','):
                            t = ts.split(':')
                            if len(t) == 2:
                                tags.append({t[0]: t[1]})
                                if t[0] == 'h':
                                    hostname = t[1]
                            else:
                                tags.append({t[0]: None})

                logger.debug(
                    'Message (metric): ' + str((metric,
                                                value,
                                                mtype,
                                                sign,
                                                rate,
                                                tags)))

                ret['metrics'].append({
                    'name': metric,
                    'value': value,
                    'type': mtype,
                    'sign': sign,
                    'rate': rate,
                    'tags': tags,
                    'hostname': hostname})

        except Exception as e:
            logger.error(
                'Invalid Message Format: "' + str(msg).rstrip() + '"')
            logger.error(str(e))
            return(None)

    if sample_count == 0 and event_count == 0:
        # if we are here, we found bupkis
        ret = {}
        logger.error(
            'Invalid Message Format: "' + str(message).rstrip() + '"')
        return(None)

    ret['counts'] = {'messages': sample_count, 'events': event_count}

    return(ret)
