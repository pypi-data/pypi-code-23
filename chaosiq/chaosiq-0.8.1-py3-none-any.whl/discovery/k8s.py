# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json
import os
import os.path
from typing import List

from chaoslib.exceptions import DiscoveryFailed
from chaoslib.types import Discovery, DiscoveredActivities, \
    DiscoveredSystemInfo, Secrets
from kubernetes import client, config
from logzero import logger

__all__ = ["discover_system"]


def discover_system() -> DiscoveredSystemInfo:
    """
    Fetch information from the current Kubernetes context.

    This requires that the current user has fetched the kubectl config before
    running the chaos discover command. Indeed, this function will bail if
    it does not find it.
    """
    logger.info("Discovering Kubernetes system")

    config_path = os.path.expanduser(
        os.environ.get('KUBECONFIG', '~/.kube/config'))

    if not os.path.exists(config_path):
        logger.warn(
            "Could not locate the default kubeconfig file.\n"
            "We cannot discover the Kubernetes system you are running.")
        return

    api = config.new_client_from_config()
    v1core = client.CoreV1Api(api)
    v1ext = client.ExtensionsV1beta1Api(api)

    ret = v1core.list_namespace(_preload_content=False)
    namespaces = ret.read()

    info = {"pods": [], "deployments": []}
    info["namespaces"] = json.loads(namespaces)
    for ns in info["namespaces"]["items"]:
        ret = v1core.list_namespaced_pod(
            namespace=ns["metadata"]["name"], _preload_content=False)
        info["pods"].append(json.loads(ret.read()))

        ret = v1ext.list_namespaced_deployment(
            namespace=ns["metadata"]["name"], _preload_content=False)
        info["deployments"].append(json.loads(ret.read()))

    return info
