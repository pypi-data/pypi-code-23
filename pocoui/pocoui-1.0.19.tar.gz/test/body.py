# coding=utf-8


import json
from hunter_cli import Hunter, open_platform
from poco.drivers.netease.internal import NeteasePoco

if __name__ == '__main__':
    tokenid = open_platform.get_api_token('poco-test')
    # hunter = Hunter(tokenid, 'g62', devid='g62_at_408d5c117d0f')
    hunter = Hunter(tokenid, 'y1', devid='y1_at_10-254-55-235')
    poco = NeteasePoco('y1', hunter)

    from airtest.core.api import connect_device

    connect_device('Android:///')
    poco('btn_phone').click()

    # print poco(visible=False).query