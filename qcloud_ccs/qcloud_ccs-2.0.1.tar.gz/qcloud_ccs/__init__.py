#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mod by wanglin@dbca.cn at 2017.10.12

import yaml
from qcloud_ccs.api import CCSAPI
from qcloud_ccs.base import CCS
import argparse

class NoAccountFoundException(BaseException):
    pass

def usage(cmd_parser):
    cmd_parser.print_help()
    exit(-1)

def get_envvars(envlist):
    arg_envvars = []
    envlist = envlist.strip().split(';')

    for prop_obj in envlist:
        prop_pair = prop_obj.split('=')
        if len(prop_pair) != 2:
            continue
        env_var = {'name': prop_pair[0], 'value': prop_pair[1]}
        arg_envvars.append(env_var)
    return arg_envvars

def get_config(f_product, f_account=None):
    # load product product from yaml
    with open(f_product) as p:
        product = yaml.load(p)

    # rewrite product.account if vars found from enviroment
    try:
        if f_account == None:
            f_account = '/etc/qcloud_ccs/account.yml'

        with open(f_account) as a:
            account = yaml.load(a)
    except:
        if not 'account' in product.keys():
            raise NoAccountFoundException('Not find account config file : %s' % f_account) from None
        else:
            account = {}
            account['account'] = product['account']
    else:
        if 'account' in product.keys():
            account['account'] = product['account']

    return account['account'], product['service'], product['node']

def main():
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("ops", nargs='?', help="Command: describe_cluster/create_node_byHour/destory_node_byHour/run_service_once/describe_service/stop_service/update_service.")
    cmd_parser.add_argument("-auth", dest="auth", help='Qcloud sdk auth config.')
    cmd_parser.add_argument("-config", dest="config", help='Qcloud sdk container config.')
    cmd_parser.add_argument("-file-version", dest="config_version", help='app config file from cmdb.')
    cmd_parser.add_argument("-file", dest="config_path", help='app config file from cmdb.')
    cmd_parser.add_argument("-container", dest="container_name", help='container name.')
    cmd_parser.add_argument("-tag",  dest="image_tag", help='app image tag from CI.')
    cmd_parser.add_argument("-replicas",  dest="replicas", help='app container replicas to run.')
    cmd_parser.add_argument("-service", dest='service_name', help="k8s service name")
    cmd_parser.add_argument("-cpu", dest="cpu", help='cpu cores of cluser node')
    cmd_parser.add_argument("-mem", dest="mem", help='mem size of cluster node')
    cmd_parser.add_argument("-envlist", dest="envlist", help='container envlist.')
    args = cmd_parser.parse_args()

    ops = args.ops
    auth = args.auth
    config = args.config
    config_version = args.config_version
    config_path = args.config_path
    container_name = args.container_name
    image_tag = args.image_tag
    replicas = args.replicas
    service_name = args.service_name
    cpu = args.cpu
    mem = args.mem
    envlist = args.envlist

    if ops is None or ops == '':
        usage(cmd_parser)

    # get config
    if config is None or config == '':
        raise OSError('No profile given: -config')
    else:
        account, service, node = get_config(config, auth)

    # if file is None, will not update configmap
    if config_path == 'None':
        config_path = None

    # container numbers
    if replicas == 'None':
        replicas = None

    # rewrite server_name if given
    if service_name is not None:
        service['service_name'] = service_name

    # rewrite cpu/mem of node instance if given
    # function: api.add_instance()
    if cpu is not None and mem is not None:
        node['cpu'] = cpu
        node['mem'] = mem

    # format env args of container
    if envlist is not None:
        arg_envvars = get_envvars(envlist)
    else:
        arg_envvars = None

    api = CCSAPI(account, service, node)

    if ops == 'run_service_once':
        instance_id = api.add_instance()
        api.modify_cluster_service_envlist(arg_envvars)
        api.restart_service()
        api.sync_wait_service_terminated()
        api.stop_service()
        api.delete_instance(instance_id)
    elif ops == 'create_node_byHour':
        instance_id = api.add_instance()
        log.info('--//create instance(%s)' % instance_id)
    elif ops == "destory_node_byHour":
        instance_id = api.get_instance_id()
        if instance_id != -1:
            api.delete_instance(instance_id)
    elif ops == 'describe_service':
        api.describe_cluster_service_info()
    elif ops == 'stop_service':
        api.stop_service()
        api.sync_wait_service_terminated()
    elif ops == 'restart_service':
        api.restart_service()
    elif ops == 'update_service':
        api.modify_cluster_service(config_version, config_path, container_name, image_tag, arg_envvars, replicas)
    elif ops == 'test':
        ccs = CCS(account, service, node)
        #code, data = ccs.Describe_ConfigVersion()
        #print(data)

        import json
        code, res = ccs.describe_cluster_service_info()
        #print(json.dumps(res, indent=2, ensure_ascii=False))

        code, data = ccs.modify_cluster_service(res)
        #print(res['volumes'])
        print(json.dumps(data, indent=2, ensure_ascii=False))

        #import codecs
        #with codecs.open('templates/application-product.properties', mode='rb', encoding='utf-8') as p:
        #    config_data = yaml.load(p)

        #code, codeDesc = ccs.CreateConfigVersion(config_data)
        #print(codeDesc)
    else:
        usage(cmd_parser)
