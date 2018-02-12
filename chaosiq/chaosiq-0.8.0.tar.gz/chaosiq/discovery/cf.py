# -*- coding: utf-8 -*-
import json
import os
import os.path
from typing import Any, Dict

from chaoslib.types import Configuration, Discovery, DiscoveredSystemInfo, \
    Secrets
from logzero import logger
import requests
import urllib3

urllib3.disable_warnings()

__all__ = ["discover_system"]


def discover_system() -> DiscoveredSystemInfo:
    """
    Fetch information from the current Cloud Foundry context.

    This requires that the current user has run `cf login` config before
    running the `chaos discover` command. Indeed, this function will bail if
    it does not find it.

    It will also bail if the access token has expired.
    """
    logger.info("Discovering Cloud Foundry system")
    cf_local_config = os.path.expanduser("~/.cf/config.json")
    if not os.path.exists(cf_local_config):
        logger.warn(
            "Could not locate a cloud coundry config file at '{s}'".format(
                s=cf_local_config))
        return

    configuration = {}
    secrets = {}
    with open(cf_local_config) as f:
        cf_conf = json.loads(f.read())
        if "AccessToken" not in cf_conf:
            logger.warn(
                "'{s}' is missing an access token, please run `cf login` "
                "and re-run the discovery command".format(
                    s=cf_local_config))
            return

        token_type, token = cf_conf["AccessToken"].split(" ", 1)
        secrets["cf_token_type"] = token_type
        secrets["cf_access_token"] = token
        configuration["cf_verify_ssl"] = not cf_conf["SSLDisabled"]
        configuration["cf_api_url"] = cf_conf["Target"]

    info = {}
    info["orgs"] = call_api("/v2/organizations", configuration, secrets).json()
    info["apps"] = call_api("/v2/apps", configuration, secrets).json()
    info["routes"] = call_api("/v2/routes", configuration, secrets).json()
    info["spaces"] = call_api("/v2/spaces", configuration, secrets).json()

    return info


def call_api(path: str, configuration: Configuration,
             secrets: Secrets, query: Dict[str, Any] = None,
             data: Dict[str, Any] = None, method: str = "GET",
             headers: Dict[str, str] = None) -> requests.Response:
    """
    Perform a Cloud Foundry API call and return the full response to the
    caller.
    """
    tokens = {
        "token_type": secrets.get("cf_token_type", "bearer"),
        "access_token": secrets.get("cf_access_token")
    }

    h = {
        "Accept": "application/json",
        "Authorization": "{a} {t}".format(
            a=tokens["token_type"], t=tokens["access_token"])
    }

    if headers:
        h.update(h)

    verify_ssl = configuration.get("cf_verify_ssl", True)
    url = "{u}{p}".format(u=configuration["cf_api_url"], p=path)
    r = requests.request(
        method, url, params=query, data=data, verify=verify_ssl, headers=h)

    request_id = r.headers.get("X-VCAP-Request-ID")
    logger.debug("Request ID: {i}".format(i=request_id))

    if r.status_code == 401:
        logger.warn(
            "\nYour Cloud Foundry session has expired, please run `cf login`\n"
            "then run the discover command again.")
    elif r.status_code > 399:
        logger.error("failed to call '{u}': {c} => {s}".format(
            u=url, c=r.status_code, s=r.text))

    return r
