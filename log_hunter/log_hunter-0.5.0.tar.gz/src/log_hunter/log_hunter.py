# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import re
import xml.etree.ElementTree as ET
from netrc import netrc

host = "hunter.melexis.com"

(username, account, password) = netrc().authenticators(host)

es = Elasticsearch([
        'https://{}:{}@{}/es/'.format(username, password, host)
    ], use_ssl=True, verify_certs=True)


def parse_key_values(s):
    items = [x.split('=') for x in s.split(", ")]
    return {k: v for [k, v] in items}


def parse_event(s):
    result = {}
    try:
        et = ET.fromstring(s)
        for k, v in et.attrib:
            result['event_' + k] = v
        for el in et:
            attribs = el.attrib
            result['event_' + attrib['key']] = attrib['value']
    except:
        # print("Unexpected error:", sys.exc_info()[0])
        pass

    return result


def parse_camel_tracing_message(msg):
    result = {}
    m = re.search('(\S*) >>> \((\S*)\) (.*) --> (.*) <<< .*Headers:\{([^}]*)\}.*, BodyType:([^,]*), Body:(.*)', msg)
    if m:
        result = {
            'id': m.group(1),
            'route': m.group(2),
            'from': m.group(3).split('@')[0],
            'to': m.group(4).split('@')[0],
            'body_type': m.group(6),
            'body': m.group(7)
        }

        result.update(parse_key_values(m.group(5)))
        body_type = m.group(6)
        body = m.group(7)
        if body_type == 'java.util.HashMap':
            result.update(parse_key_values(body))
        elif body_type == 'String' or body_type == 'com.melexis.dto.event.EventVO':
            result.update(parse_event(body))
        elif body_type == 'java.util.ArrayList':
            pass  # ignore body
        elif body_type == 'com.google.common.collect.Lists.TransformingRandomAccessList':
            pass  # ignore body
        else:
            # print('unknown body type: {} --> {}'.format(body_type, body))
            pass
    else:
        pass
        # print(msg)
    return result


def match_message_results(term, image=None, after='now', before='now-1h', env='prod'):
    """
    Return parsed message results as a dict from an image in an interval

    This method searches hunter for messages which match a specific term in the message text
    for a given docker image.

    This satisfies the common use case of matching the logs of a certain service as the service
    is usually deployed with the same image on the different kubernetes nodes.

    When specifying the empty string, all messages are returned giving the same effect as
    consulting a classic logfile. It is just all the loglines in chronological order between
    the start and end of the interval.

    :param term: a term to match specific messages
    :param image: a term used to match the docker image which generates the log
    :param after: start of the interval
    :param before: end of the interval
    :return: a list of dictionaries with the parsed fields of the loglines.

    """
    search = Search(using=es, index='filebeat-*')

    queries = []
    if term:
        queries.append(Q("match", message=term))
    if image:
        queries.append(Q("match", image_name=image))
    if env:
        queries.append(Q("match", env=env))

    queries.append(Q({"range": {'@timestamp':{'lte': before, 'gt': after}}}))
    s = search.query(Q("bool", must=queries)).params(request_timeout=60)

    results = []
    for hit in s.scan():
        result = {}
        add_field_to_result(hit, '@timestamp', result)
        add_field_to_result(hit, 'container_name', result)
        add_field_to_result(hit, 'host_name', result)
        add_field_to_result(hit, 'threadId', result)
        add_field_to_result(hit, 'message', result)
        #result.update(parse_camel_tracing_message(message))
        results.append(result)

    return results

def add_field_to_result(hit, term, result):
    if term in hit:
        result[term] = hit[term]
