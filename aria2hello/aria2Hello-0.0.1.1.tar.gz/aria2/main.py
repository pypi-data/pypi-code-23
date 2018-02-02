# -*- coding: utf-8 -*-
import uuid
import sys
import logging
from aria2.controller.aria2_websocket import Aria2WebSocket
import qrcode_test
import hashlib


def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac


def main(argv):
    logging.basicConfig(filename='logger.log', level=logging.INFO)
    device_id = None
    did = None
    try:
        did = open('did.id', 'rw')
        device_id = did.read().strip()
        if not device_id:
            init_device_id()
            return
    except IOError:
        init_device_id()
        return
    finally:
        if did:
            did.close()
    if argv is None or len(argv) < 2:
        print('Usage: Aria2Controller ip:port password\n Aria2Controller 127.0.0.1:6800 2345667')
    else:
        ip_port = argv[1]
        ip_port_array = ip_port.split(':')
        ip = ip_port_array[0]
        port = ip_port_array[1]
        password = None
        if len(argv) == 3:
            password = argv[2]
        
        logging.info('正在连接到aria2 ip:%s 端口:%s' % (ip, port))
        controller = Aria2WebSocket(ip=ip, port=port, password=password, device_id=device_id)
        # controller.add_uri('http://zt.bdinfo.net/speedtest/wo3G.rar')
        # controller.remove('a7f228')
        controller.connect_aria2()


def init_device_id():
    did = None
    try:
        did = open('did.id', 'w')
        device_id = uuid.uuid1().__str__()
        m = hashlib.md5()
        m.update(device_id)
        device_id = m.hexdigest()
        did.write(device_id)
    except IOError:
        logging.error("did.id 写入失败，请确认是否有权限")
        return
    finally:
        if did:
            did.close()
    
    print "step.1 使用微信扫码关注下载摇控器"
    print qrcode_test.get_qrcode_by_text('http://weixin.qq.com/r/Gjrbw67EmfPmreqg928I')
    print "\n"
    print "step.2 点击欢迎消息打开设备绑定页面\n"
    print "step.3 输入设备ID:{}或扫码绑定\n".format(device_id)
    print qrcode_test.get_qrcode_by_text(device_id)


if __name__ == '__main__':
    main(sys.argv)
