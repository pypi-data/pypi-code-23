#!/usr/bin/env python3

import argparse
import io
import os
import sys
import json
import csv
import math
import threading
import http.client
import urllib
from datetime import datetime
import collections
import boto3
import botocore

import pkg_resources
from jsonschema.validators import Draft4Validator
import singer

logger = singer.get_logger()
s3 = None

def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        logger.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()

def persist_lines(filename, lines):
    state = None
    schemas = {}
    key_properties = {}
    headers = {}
    validators = {}

    now = datetime.now().strftime('%Y%m%dT%H%M%S')

    for line in lines:
        try:
            o = json.loads(line)
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(line))
            raise

        if 'type' not in o:
            raise Exception("Line is missing required key 'type': {}".format(line))
        t = o['type']

        if t == 'RECORD':
            if 'stream' not in o:
                raise Exception("Line is missing required key 'stream': {}".format(line))
            if o['stream'] not in schemas:
                raise Exception("A record for stream {} was encountered before a corresponding schema".format(o['stream']))

            schema = schemas[o['stream']]
            validators[o['stream']].validate(o['record'])

            with open(filename, 'a') as f:
                f.write(json.dumps(o['record']) + '\n')

            state = None
        elif t == 'STATE':
            logger.debug('Setting state to {}'.format(o['value']))
            state = o['value']
        elif t == 'SCHEMA':
            if 'stream' not in o:
                raise Exception("Line is missing required key 'stream': {}".format(line))
            stream = o['stream']
            schemas[stream] = o['schema']
            validators[stream] = Draft4Validator(o['schema'])
            if 'key_properties' not in o:
                raise Exception("key_properties field is required")
            key_properties[stream] = o['key_properties']
        else:
            raise Exception("Unknown message type {} in message {}"
                            .format(o['type'], o))

    return state

def download_to_s3(local_file, s3_bucket, s3_file):
    if s3_bucket is None or s3_file is None:
        return

    logger.info('Pulling s3 file: {}/{}'.format(s3_bucket, s3_file))
    try:
        s3.Bucket(s3_bucket).download_file(s3_file, local_file)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.info("s3 object doesn't exist")
        else:
            raise e

def upload_to_s3(local_file, s3_bucket, s3_file):
    if s3_bucket is None or s3_file is None:
        return

    s3.Bucket(s3_bucket).upload_file(local_file, s3_file)

def main():
    global s3

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as input:
            config = json.load(input)
    else:
        config = {}

    if 's3_endpoint' in config:
        s3 = boto3.resource('s3', endpoint_url=config['s3_endpoint'])
    else:
        s3 = boto3.resource('s3')


    input = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    filename = config.get('filename', 'output.sample.json')
    s3_bucket = config.get('s3_bucket', None)
    s3_file = config.get('s3_file', None)

    download_to_s3(filename, s3_bucket, s3_file)
    state = persist_lines(filename, input)
    upload_to_s3(filename, s3_bucket, s3_file)

    emit_state(state)
    logger.debug("Exiting normally")


if __name__ == '__main__':
    main()
