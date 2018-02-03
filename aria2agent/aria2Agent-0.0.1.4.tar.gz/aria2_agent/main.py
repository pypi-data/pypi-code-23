# -*- coding: utf-8 -*-
import uuid
import sys
import logging
from aria2_agent.websocket_rpc.aria2_websocket import Aria2WebSocket
from aria2_agent.api.aria2_api import Aria2Api
from agent import Agent
import hashlib
import ConfigParser
import os
import argparse



def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', required=True, help='Path of config file. Reference: http://www.pocketdigi.com/')
    argv = sys.argv
    if argv is None or len(argv) < 2:
        parser.print_help()
        return
    args = parser.parse_args()
    
    config_path = args.c
    cf = ConfigParser.ConfigParser()
    cf.read(config_path)
    try:
        rpc_host = cf.get('aria2', 'rpc-host')
        rpc_port = cf.get('aria2', 'rpc-port')
        rpc_secret = cf.get('aria2', 'rpc-secret')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError), e:
        print('配置文件错误 %s' % str(e))
        return
    try:
        device_id = cf.get('agent', 'device_id')
        if not device_id:
            device_id = init_device_id(config_path, cf)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        device_id = init_device_id(config_path, cf)
    
    print(rpc_host, rpc_port, device_id)
    
    logging.basicConfig(filename='log.log', level=logging.INFO)
    
    agent = Agent(rpc_host=rpc_host, rpc_port=rpc_port, rpc_secret=rpc_secret, device_id=device_id)
    agent.connect()


def init_device_id(config_path, cf):
    """初始化设备id"""
    device_id = uuid.uuid1().__str__()
    m = hashlib.md5()
    m.update(device_id)
    device_id = m.hexdigest()[8:24]
    if not cf.has_section('agent'):
        cf.add_section('agent')
    cf.set('agent', 'device_id', device_id)
    with open(config_path, "w+") as f:
        cf.write(f)
        f.close()
    return device_id


if __name__ == '__main__':
    main()
