# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.sensor_events.base_event import SensorEvent


class HoneytokenSensorEvent(SensorEvent):
    def __init__(self, remote_address, token_id):
        super(HoneytokenSensorEvent, self).__init__("honeytoken")
        self["id"] = token_id
        self["remote_addr"] = remote_address

    def post_process(self):
        pass
