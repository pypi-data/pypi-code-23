# coding=utf-8
import logging
import requests
from requests.auth import HTTPBasicAuth

from mailchimp.config import mailchimp_config as cfg
from mailchimp.exceptions import ObjectNotFound

logger = logging.getLogger(__name__)


class Request(object):
    @classmethod
    def get_headers(cls):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    @classmethod
    def delete(cls, url):
        logging.debug("DELETE: %s" % url)
        if url.startswith("http"):
            response = requests.delete(url, auth=HTTPBasicAuth('username', cfg.api_key),
                                       headers=Request.get_headers())
        else:
            response = requests.delete("%s%s" % (cfg.get_server_url(), url),
                                       auth=HTTPBasicAuth('username', cfg.api_key), headers=Request.get_headers())
        if response.status_code != 204 and response.content:
            logging.debug(response.json())
        response.raise_for_status()
        return response

    @classmethod
    def get(cls, url, params={}):
        logging.debug("GET: url: %s, params: %s" % (url, params))
        if url.startswith("http"):
            response = requests.get(url, params, auth=HTTPBasicAuth('username', cfg.api_key),
                                    headers=Request.get_headers())
        else:
            response = requests.get("%s%s" % (cfg.get_server_url(), url), params,
                                    auth=HTTPBasicAuth('username', cfg.api_key), headers=Request.get_headers())

        if response.content:
            logging.debug(response.json())
        if response.status_code == 404:
            raise ObjectNotFound
        else:
            response.raise_for_status()
        return response

    @classmethod
    def put(cls, url, data):
        logger.debug("PUT: url: %s, data: %s" % (url, data))
        if url.startswith("http"):
            response = requests.put(url, json=data, auth=HTTPBasicAuth('username', cfg.api_key),
                                    headers=Request.get_headers())
        else:
            response = requests.put("%s%s" % (cfg.get_server_url(), url), json=data,
                                    auth=HTTPBasicAuth('username', cfg.api_key), headers=Request.get_headers())
        if response.content:
            logging.debug(response.json())
        response.raise_for_status()
        return response

    @classmethod
    def post(cls, url, data):
        logger.debug("POST: url: %s, data: %s" % (url, data))
        if url.startswith("http"):
            response = requests.post(url, json=data, auth=HTTPBasicAuth('username', cfg.api_key),
                                     headers=Request.get_headers())
        else:
            response = requests.post("%s%s" % (cfg.get_server_url(), url), json=data,
                                     auth=HTTPBasicAuth('username', cfg.api_key), headers=Request.get_headers())
        if response.content:
            logging.debug(response.json())
        response.raise_for_status()
        return response
