#!/usr/bin/env python3

import json
from QcloudApi.qcloudapi import QcloudApi
from qcloud_ccs.log import log

class ServiceConfigureException(Exception):
    pass

class CCS:

    def __init__(self, account, service, node):
        # get account info and init QcloudApi
        param = {
            'Region': service['region'],
            'secretId': account['secret_id'],
            'secretKey': account['secret_key'],
            'method': 'post'
        }
        self._service = QcloudApi('ccs', param)

        # set service vars
        self._cluster_id = service['cluster_id']
        self._namespace = service['namespace']
        self._service_name = service['service_name']
        self._config_id = service['config_id']
        #self._config_name = service['config_name']

        # set node vars
        self._node = node

    def describe_cluster_instance(self):
        """
        action: DescribeClusterInstances
        desc: 本接口 (DescribeClusterInstances) 用于查询集群节点，该接口返回集群内节点信息
        :return:

        """
        action = 'DescribeClusterInstances'

        params = {
            'clusterId': self._cluster_id
        }

        res = json.loads(self._service.call(action, params))

        ret_data = {
            'isNormal': False,
            'message': res['message']
        }

        if res['code'] != 0:
            log.error(res['message'])
            res['code'] = -1
            return res['code'], ret_data

        total_count = res['data']['totalCount']
        ret_data['totalCount'] = total_count
        if total_count == 1:
            node0 = res['data']['nodes'][0]

            if node0['isNormal'] == 1:
                is_normal = True
            else:
                is_normal = False

            ret_data['isNormal'] = is_normal
            ret_data['instanceId'] = node0['instanceId']
            ret_data['cpu'] = node0['cpu']
            ret_data['mem'] = node0['mem']
            ret_data['osImage'] = node0['osImage']
            ret_data['createdAt'] = node0['createdAt']
            ret_data['lanIp'] = node0['lanIp']
            ret_data['wanIp'] = node0['wanIp']
        elif total_count > 1:
            log.warning('cluster instance count is not std.')
            res['code'] = -1
        else:
            log.warning("instance count value is 0")

        return res['code'], ret_data

    def delete_cluster_instance(self, instance_id):
        """
        action: DeleteClusterInstances
        desc: 本接口 (DeleteClusterInstances) 用于为删除集群节点。
        **NOTE** 当集群status为Running，Isolated，Abnormal时，才能调用此接口。
        :param instance_id:
        :return:
        """
        action = 'DeleteClusterInstances'

        params = {
            'clusterId': self._cluster_id,
            'instanceIds.0': instance_id
        }

        res = json.loads(self._service.call(action, params))
        return res['code'], res['data']

    def add_cluster_instance(self):
        """
        action: AddClusterInstances
        详细配置建：https://www.qcloud.com/document/product/213/2177#5.-.E5.8D.8E.E5.8C.97.E5.9C.B0.E5.8C.BA(.E5.8C.97.E4.BA.AC)-.E5.8C.97.E4.BA.AC.E4.BA.8C.E5.8C.BA22
        :param cpu:
        :param mem:
        :return: code, data
        """
        action = 'AddClusterInstances'

        param = {
            'clusterId': self._cluster_id,
            'zoneId': 800002,
            'cpu': self._node['cpu'],
            'mem': self._node['mem'],
            'instanceType': 'CVM.S2',
            'cvmType': 'PayByHour',
            'bandwidthType': 'PayByHour',
            'bandwidth': 5,
            'wanIp': 1,
            'subnetId': self._node['subnet_id'],
            'isVpcGateway': 0,
            'storageSize': 0,
            'rootSize': 20,
            'goodsNum': 1,
            'password': 'Ywjn123xylz!@#',
            'sgId': self._node['sg_id']
        }

        res = json.loads(self._service.call(action, param))

        ret_data = {
            'message': res['message']
        }

        if res['code'] != 0:
            log.error(res['message'])
            return res['code'], ret_data

        instances_size = len(res['data']['instanceIds'])
        if instances_size == 1:
            ret_data['instanceId'] = res['data']['instanceIds'][0]
            ret_data['requestId'] = res['data']['requestId']
        else:
            log.error("this cluster is not std ci cluster")
            res['code'] = -1

        return res['code'], ret_data

    def describe_service_instance(self):
        """
        action: DescribeServiceInstance
        本接口 (DescribeServiceInstance) 用于查询服务的实例列表。
        :return:
        """
        action = 'DescribeServiceInstance'

        params = {
            'clusterId': self._cluster_id,
            'serviceName': self._service_name,
            'namespace': self._namespace
        }

        res = json.loads(self._service.call(action, params))

        ret_data = {
            'message': res['message']
        }

        if res['code'] != 0:
            log.error(res['message'])
            return res['code'], ret_data

        total_count = res['data']['totalCount']
        ret_data['totalCount'] = total_count

        if total_count == 1:
            instance0 = res['data']['instances'][0]
            ret_data['status'] = instance0['status']
            ret_data['message'] = instance0['reason']
            if ret_data['status'] == 'Running':
                ret_data['ip'] = instance0['ip']
                ret_data['createdAt'] = instance0['createdAt']
                ret_data['image'] = instance0['containers'][0]['image']
                ret_data['containerId'] = instance0['containers'][0]['containerId']
        else:
            res['message'] = "total count != 1, please check cluster and service"

        return res['code'], ret_data

    def describe_cluster_service_info(self):

        action = 'DescribeClusterServiceInfo'

        params = {
            'clusterId': self._cluster_id,
            'serviceName': self._service_name,
            'namespace': self._namespace
        }

        res = json.loads(self._service.call(action, params))

        ret_data = {
            'message': res['message']
        }

        if res['code'] != 0 or 'data' not in res:
            log.error(res['message'])
            return res['code'], ret_data

        service = res['data']['service']
        service_name = service['serviceName']
        if service_name != self._service_name:
            return -1, ret_data

        ret_data.update(service)
        ret_data['serviceName'] = service_name
        if 'reason' in service:
            ret_data['message'] = service['reason']
        ret_data['status'] = service['status']

        if 'portMappings' in service:
            ret_data['portMappings'] = service['portMappings']

        return res['code'], ret_data

    def modify_cluster_service(self, service):
        action = 'ModifyClusterService'

        params = {
            'clusterId': self._cluster_id,
            'serviceName': self._service_name,
            'strategy': service['strategy'],
            'minReadySeconds': 60,
            'replicas': service['desiredReplicas'],
            'accessType': service['accessType'],
            'containers': service['containers'],
            'portMappings': service['portMappings'],
            'volumes': service['volumes'],
            'namespace': service['namespace'],
            'subnetId': service['subnetId']
        }

        #log.info(json.dumps(params, indent=2, ensure_ascii=False))
        res = json.loads(self._service.call(action, params))

        return res['code'], res

    def modify_service_replicas(self, scale_to):
        """
        action: ModifyServiceReplicas
        本接口 (ModifyServiceReplicas) 用于修改服务的容器数量

        当scale_to为0时会停止服务，
        当scale_to为1时会启动服务。

        :param scale_to:
        :return:
        """
        action = 'ModifyServiceReplicas'

        params = {
            'clusterId': self._cluster_id,
            'namespace': self._namespace,
            'serviceName': self._service_name,
            'scaleTo': scale_to
        }

        ret_data = json.loads(self._service.call(action, params))
        return ret_data['code'], ret_data

    def describe_cluster_task_result(self, request_id):
        """
        action: DescribeClusterTaskResult
        本接口 (DescribeClusterTaskResult)查询异步任务结果
        :param request_id:
        :return:
        """
        action = 'DescribeClusterTaskResult'

        params = {
            'clusterId': self._cluster_id,
            'requestId': request_id
        }

        res = json.loads(self._service.call(action, params))

        return res['code'], res['data']

    def Describe_ConfigVersion(self):
        """
        action: DescribeClusterTaskResult
        本接口 (DescribeClusterTaskResult)查询配置文件版本
        :param configId:
        :return:
        """
        action = 'DescribeConfigVersion'

        params = {
            'configId': self._config_id
        }

        res = json.loads(self._service.call(action, params))

        return res['code'], res['data']

    def CreateConfigVersion(self, config_version, config_data):
        """
        action: CreateConfigVersion
        本接口 (CreateConfigVersion)查询配置文件
        :param configId, version;
        :return:
        """
        #action = 'CreateConfigVersion'
        action = 'CreateConfigVersion'

        params = {
            'configId': self._config_id,
            'version': config_version,
            'data': config_data
        }

        # print(yaml.dump(config_data, default_flow_style=False))
        res = json.loads(self._service.call(action, params))

        return res['code'], res['message']