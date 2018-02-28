"""Elasticsearch utilities"""

from elasticsearch import Elasticsearch, TransportError
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import streaming_bulk
import contextlib
import logging
import os
import time
import uuid


HOSTNAME = os.getenv('ELASTICSEARCH_ENDPOINT', 'localhost:9200')


def basic_client():
    """Returns an Elasticsearch basic client that is responsive
    to the environment variable ELASTICSEARCH_ENDPOINT"""
    es_connected = False
    while not es_connected:
        try:
            ES = Elasticsearch(
                hosts=[HOSTNAME]
            )
            es_connected = True
        except TransportError as e:
            logging.info('Not yet connected: %s, sleeping for 1s', e)
            time.sleep(1)
    return ES


def indices_client():
    """Returns an Elasticsearch indices client that is responsive
    to the environment variable ELASTICSEARCH_ENDPOINT"""
    es_connected = False
    while not es_connected:
        try:
            ES = Elasticsearch(
                hosts=[HOSTNAME]
            )
            es_connected = True
        except TransportError as e:
            logging.info('Not yet connected: %s, sleeping for 1s', e)
            time.sleep(1)
    return IndicesClient(ES)


def create_index(index_name, index_config, client):
    """Creates an index with a given configuration

    Args:
        index_name (str): Name of the index you want to create
        index_config (dict) configuration for the index
        client (Elasticsearch.IndicesClient) the Elasticsearch client
    """
    client.create(index=index_name, body=index_config)


def get_index_from_alias(alias_name, index_client=None):
    """Retrieve the base index name from an alias

    Args:
        alias_name (str) Name of the alias
        index_client (Elasticsearch.IndicesClient) an Elasticsearch index
            client. Optional, will create one if not given

    Returns: (str) Name of index
    """
    index_client = index_client or indices_client()
    if not index_client.exists_alias(name=alias_name):
        return None
    return list(index_client.get_alias(name=alias_name).keys())[0]


def atomic_swap(alias_name, new_index_name, index_client):
    """Points an alias to a new index, then delete the old index if needed

    Uses client.update_aliases to perform this with zero downtime

    Args:
        alias_name (str) Name of the alias
        new_index_name (str) The new index that the alias should point to
        index_client (Elasticsearch.IndicesClient) Elasticsearch index client
    """
    logging.info('Performing atomic index alias swap')
    if index_client.exists_alias(name=alias_name):
        old_index_name = get_index_from_alias(alias_name, index_client)
        logging.info('Removing old as well as adding new')
        actions = {'actions': [
            {'remove': {'index': old_index_name, 'alias': alias_name}},
            {'add': {'index': new_index_name, 'alias': alias_name}}
        ]}
        index_client.update_aliases(body=actions)
        index_client.delete(index=old_index_name)
    else:
        logging.info('Old alias not found, only adding new')
        actions = {'actions': [
            {'add': {'index': new_index_name, 'alias': alias_name}}
        ]}
        index_client.update_aliases(body=actions)


@contextlib.contextmanager
def zero_downtime_index(index_name, index_config):
    """Context manager to create a new index based on a given alias,
    allow the caller to index it, and then point the alias to the new index

    Args:
        index_name (str) Name of an alias that should point to the new index
        index_config (dict) Configuration for the new index

    Yields: (name) The full name of the new index
    """
    client = indices_client()
    temporary_name = index_name + '_' + str(uuid.uuid4())
    logging.info('creating index with config %s', index_config)
    create_index(temporary_name, index_config, client)
    try:
        yield temporary_name
        atomic_swap(index_name, temporary_name, client)
    except Exception:
        logging.error(
            'deleting temporary index %s due to error:',
            temporary_name,
            exc_info=True
        )
        client.delete(index=temporary_name)


class ElasticsearchIndexerBase(object):
    def __init__(self, s3_conn, es_client):
        """
        Base class for Elasticsearch indexers

        Subclasses implement the index setting definition and transformation of data,
        The base class handles index management and bulk indexing with ES

        Args:
            s3_conn - a boto s3 connection
            es_client - an Elasticsearch indices client
        """
        self.s3_conn = s3_conn
        self.es_client = es_client

    def index_config(self):
        """Combines setting and mapping config into a full index configuration
        Returns: dict
        """
        return {
            'settings': self.settings,
            'mappings': self.mappings
        }

    def replace(self):
        """Replace index with a new one
        zero_downtime_index for safety and rollback
        """
        with zero_downtime_index(self.alias_name, self.index_config()) as target_index:
            self.index_all(target_index)

    def append(self):
        """Index documents onto an existing index"""
        target_index = get_index_from_alias(self.alias_name)
        if not target_index:
            self.replace()
        else:
            self.index_all(target_index)

    def index_all(self, index_name):
        """Index all available documents, using streaming_bulk for speed
        Args:

        index_name (string): The index
        """
        oks = 0
        notoks = 0
        for ok, item in streaming_bulk(
            self.es_client,
            self._iter_documents(index_name)
        ):
            if ok:
                oks += 1
            else:
                notoks += 1
        logging.info(
            "Import results: %d ok, %d not ok",
            oks,
            notoks
        )
