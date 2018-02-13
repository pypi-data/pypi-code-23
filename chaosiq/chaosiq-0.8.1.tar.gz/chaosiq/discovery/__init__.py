# -*- coding: utf-8 -*-
from chaoslib.types import DiscoveredSystemInfo
from logzero import logger

__all__ = ["discover_system_info"]


def discover_system_info(target: str) -> DiscoveredSystemInfo:
    """
    Inspect the targeted system and return information.

    For each subsystem, this requires that the current user can talk to the
    target.
    """
    if target == "kubernetes":
        from chaosiq.discovery.k8s import discover_system
    elif target == "cloud-foundry":
        from chaosiq.discovery.cf import discover_system
    else:
        logger.warn("ChaosIQ does not know how to explore system: {}".format(
            target
        ))
        return

    return discover_system()
