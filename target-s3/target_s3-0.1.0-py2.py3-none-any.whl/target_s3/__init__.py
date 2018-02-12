import io
import os
import sys
import datetime
import json

import boto3
import botocore
import singer

from jsonschema.validators import Draft4Validator
from singer import logger, utils

LOGGER = logger.get_logger()
FILENAME = 'output.json'
S3 = None
CONFIG = {}

def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        LOGGER.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()

def persist_lines(lines):
    state = None
    schemas = {}
    key_properties = {}
    headers = {}
    validators = {}

    now = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')

    for line in lines:
        try:
            o = json.loads(line)
        except json.decoder.JSONDecodeError:
            LOGGER.error("Unable to parse:\n{}".format(line))
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

            with open(FILENAME, 'a') as f:
                f.write(json.dumps(o['record']) + '\n')

            state = None
        elif t == 'STATE':
            LOGGER.debug('Setting state to {}'.format(o['value']))
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

def download_to_s3(s3_bucket, s3_file):
    if s3_bucket is None:
        return

    LOGGER.info('Pulling s3 file: s3://{}/{}'.format(s3_bucket, s3_file))
    try:
        S3.Bucket(s3_bucket).download_file(s3_file, FILENAME)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            LOGGER.info("s3 object doesn't exist")
        else:
            raise e

def upload_to_s3(s3_bucket, s3_file):
    if s3_bucket is None:
        return

    LOGGER.info('Pushing s3 file: s3://{}/{}'.format(s3_bucket, s3_file))
    S3.Bucket(s3_bucket).upload_file(FILENAME, s3_file)

def main():
    global S3

    required_keys = ['summoner_name', 'region', 'queue', 'season']
    args = utils.parse_args(required_keys)

    CONFIG.update(args.config)

    if 's3_endpoint' in CONFIG:
        S3 = boto3.resource('s3', endpoint_url=CONFIG['s3_endpoint'])
    else:
        S3 = boto3.resource('s3')


    input = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    s3_bucket = CONFIG.get('s3_bucket', None)
    s3_file = '{}/{}/{}.json'.format(
        CONFIG['season'],
        CONFIG['summoner_name'],
        CONFIG['queue'],
    )

    download_to_s3(s3_bucket, s3_file)
    state = persist_lines(input)
    upload_to_s3(s3_bucket, s3_file)

    emit_state(state)
    LOGGER.debug("Exiting normally")


if __name__ == '__main__':
    main()
