# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import re

from future.backports.urllib.parse import urlsplit

from tcell_agent.policies.base_policy import TCellPolicy
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent


def wildcard_re(item):
    return re.compile("^{}$".format(re.escape(item).replace("\\*", ".*")),
                      flags=re.IGNORECASE)


def portless(host):
    if host:
        return host.split(':')[0]
    else:
        return None


class HttpRedirectPolicy(TCellPolicy):
    def __init__(self, policy_json=None):
        super(HttpRedirectPolicy, self).__init__()
        self.enabled = False
        self.block = False
        self.whitelist = []
        self.data_scheme_allowed = False
        if policy_json is not None:
            self.load_from_json(policy_json)

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        policy_data_json = policy_json.get("data")
        if policy_data_json:
            self.enabled = policy_data_json.get("enabled", False)
            self.block = policy_data_json.get("block", False)
            whitelist = policy_data_json.get("whitelist", [])
            self.whitelist = [wildcard_re(item) for item in whitelist]
            self.data_scheme_allowed = policy_data_json.get("data_scheme_allowed", [])

    def process_location(self,
                         remote_address,
                         method,
                         from_domain,
                         from_full_path,
                         status_code,
                         redirect_url,
                         user_id=None,
                         session_id=None,
                         route_id=None):
        if not self.enabled:
            return redirect_url

        from tcell_agent.agent import TCellAgent

        parsed_redirect_url = urlsplit(redirect_url)
        location_host = parsed_redirect_url.hostname  # returns portless hostname
        from_domain_portless = portless(from_domain)

        if parsed_redirect_url.scheme and parsed_redirect_url.scheme.lower() == "data":
            if self.data_scheme_allowed:
                return redirect_url

            location_host = redirect_url.split(",")[0]

        else:

            if not location_host:
                return redirect_url

            if location_host == from_domain_portless:
                return redirect_url

            for item in self.whitelist:
                if item.match(location_host) or item.match('www.' + location_host):

                    return redirect_url

            location_host = location_host

        event = RedirectSensorEvent(
            remote_address,
            method,
            from_domain_portless,
            from_full_path,
            status_code,
            location_host,
            user_id,
            session_id,
            route_id)

        TCellAgent.send(event)

        if self.block:
            return "/"

        return redirect_url
