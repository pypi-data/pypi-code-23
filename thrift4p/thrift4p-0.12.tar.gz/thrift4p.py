# encoding:utf-8

import sys
import re
import os
from kazoo.client import KazooClient
from random import choice

from thrift.transport import TSocket    
from thrift.transport import TTransport    
from thrift.protocol import TBinaryProtocol

def get_api_server(zkAddr):
    """获取所有的api以及对应的服务器
    @return: api与服务器的映射
    """
    
    zk = KazooClient(hosts=zkAddr)
    zk.start()
    apis = zk.get_children('/rpc/thrift/')
    
    api2ip_port_set = dict()
    api2path_set = dict()
    
    for api in apis:
        path = '/rpc/thrift/' + api + "/server"
        
        ip_port_set = set()
        path_set = set()
        
        traverse_list(path,zk,ip_port_set,path_set)
        
        api2ip_port_set[api] = ip_port_set
        api2path_set[api] = api2path_set
        
    zk.stop()
    
    return api2ip_port_set,api2path_set
    
def traverse_list(path,zk,ip_port_set,path_set):
    """递归遍历zookeeper目录
    @param path: 根目录
    @param zk: zookeeper实例
    @param ip_port_set: 保存的服务器集合
    @param path_set: 保存的zookeeper路径集合
    """
    
    if zk.exists(path):
        children = zk.get_children(path)
        
        if len(children) == 0:

            if re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,3}",path.split("/")[-1]):
                path_set.add(path)
                ip_port_set.add(path.split("/")[-1])
                    
            return 
        
        for sub_path in children:
            sub_path = path + "/" + sub_path        
            traverse_list(sub_path,zk,ip_port_set,path_set)

def generate_client_from_zk(api,zkAddr):
    """根据api生成client"""
    
    api2ip_port_set,api2path_set = get_api_server(zkAddr)
    
    if api2ip_port_set.get(api) is None:
        raise KeyError(api)
    
    ip_port_set = api2ip_port_set[api]
    if len(ip_port_set) == 0:
        raise KeyError("no available server for " + api)
    
    server_port = choice(list(ip_port_set))
    
    ip = server_port.split(":")[0]
    port = int(server_port.split(":")[1])
    
    #print server_port
    # Make socket    
    transport = TSocket.TSocket(ip, port)    
    
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TFramedTransport(transport)
    
    # Wrap in a protocol    
    protocol = TBinaryProtocol.TBinaryProtocol(transport)    
    
    # Create a client to use the protocol encoder
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/gen-py')
    service_name = api.split(".")[-1]
    
    thrift_package_name = get_thrift_file_name(service_name)
    
    #print thrift_package_name,service_name
    if thrift_package_name is None:
        raise NameError(service_name)
    
    service = __import__(thrift_package_name + "." + service_name, globals(), locals(), [service_name,], -1)
    
    client = service.Client(protocol)   
    
    #print dir(client)
    
    # Connect!    
    transport.open()
    
    return client

def get_thrift_file_name(service_name):
    """从thrift文件夹中根据service名查找对应的package名
    thrift --gen py -out ../gen-py DmOperationHubService.thrift
    """
    
    thrift_file_name = None
    
    path = os.path.dirname(os.path.realpath(__file__)) + "/thrift_files"
    for filename in os.listdir(path):
    
        if os.path.isfile(path + "/" + filename):
            content = "\n".join(open(path + "/" + filename).readlines())
            
            if content.find(service_name) != -1:
                thrift_file_name = filename.split(".")[0]
                break
            
    return thrift_file_name
    