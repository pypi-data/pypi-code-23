#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# by seanly@aliyun.com at 2017.07.11

import time
import asyncio
import codecs, yaml
from qcloud_ccs.log import log
from qcloud_ccs.base import CCS

class ArgumentException(BaseException):
    pass


class QcloudApiException(BaseException):
    pass


class ServiceConfigureException(QcloudApiException):
    pass


class DescribeClusterInstanceException(QcloudApiException):
    pass


class AddClusterInstanceException(QcloudApiException):
    pass


class DeleteClusterInstanceException(QcloudApiException):
    pass


class DescribeServiceInstanceException(QcloudApiException):
    pass


class ModifyServiceReplicasException(QcloudApiException):
    pass


class DescribeClusterServiceInfoException(QcloudApiException):
    pass


class ModifyClusterServiceException(QcloudApiException):
    pass


class CCSAPI:

    def __init__(self, account, service, node):
        self._ccs = CCS(account, service, node)
        self._node = node

        # set service vars
        self._cluster_id = service['cluster_id']
        self._namespace = service['namespace']
        self._service_name = service['service_name']
        self._config_id = service['config_id']
        #self._config_name = service['config_name']
        #self._image_url = service['image_url']

    @asyncio.coroutine
    def wait_task_complete(self, request_id):

        while True:
            yield from asyncio.sleep(10)
            code, data = self._ccs.describe_cluster_task_result(request_id)
            if code != 0:
                log.error("describe cluster task result api error: %s" % data['message'])
                continue

            if 'status' not in data:
                continue

            if data['status'] == 'running':
                log.info('task(%s) status: %s' % (request_id, data['status']))
                continue
            else:
                log.info('task(%s) status: %s' % (request_id, data['status']))
                break

    @asyncio.coroutine
    def describe_cluster_instance(self):

        while True:
            yield from asyncio.sleep(10)

            code, data = self._ccs.describe_cluster_instance()
            if code != 0:
                log.error("describe cluster task result api error: %s" % data['message'])
                continue

            if 'isNormal' in data and data['isNormal']:
                log.info('instance(%s) ready.' % data['instanceId'])
                return

    @asyncio.coroutine
    def describe_cluster_instance_clean(self):

        while True:
            yield from asyncio.sleep(10)

            code, data = self._ccs.describe_cluster_instance()
            if code != 0:
                log.error("describe cluster task result api error: %s" % data['message'])
                continue

            if 'totalCount' in data and data['totalCount'] == 0:
                log.info('instance clean over.')
                break

    def get_instance_id(self):
        log.info('describe cluster instance info ....')
        code, describe_data = self._ccs.describe_cluster_instance()
        if code != 0:
            raise DescribeClusterInstanceException('cluster instance info error: %s' % describe_data['message'])

        log.info('checkout instance status...')
        # DONE: check instance isNormal is
        if 'isNormal' in describe_data and not describe_data['isNormal']:
            log.warning('cluster instance count is 0.')
            return -1

        return describe_data['instanceId']

    def add_instance(self):
        log.info('describe cluster instance info ....')
        code, describe_data = self._ccs.describe_cluster_instance()
        if code != 0:
            raise DescribeClusterInstanceException('cluster instance info error: %s' % describe_data['message'])

        if 'totalCount' in describe_data and describe_data['totalCount'] == 0:
            log.info('create instance: cpu-%d core, mem-%dG' % (self._node['cpu'], self._node['mem']))
            code, add_data = self._ccs.add_cluster_instance()
            if code != 0:
                raise AddClusterInstanceException('add cluster instance error: %s' % add_data['message'])

            log.info('--//wait instance ready.....')

            if 'requestId' in add_data:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.wait_task_complete(add_data['requestId']))
                log.info('instance(%s) ready ok.' % add_data['instanceId'])
            else:
                raise AddClusterInstanceException('add cluster ret data error, is not requestId')

            return add_data['instanceId']

        log.info('checkout instance status...')
        # DONE: check instance isNormal is
        if 'isNormal' in describe_data and not describe_data['isNormal']:
            log.info('--//wait instance status ready....')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.describe_cluster_instance())
            log.info('--// instance(%s) status ready ok.' % describe_data['instanceId'])

        return describe_data['instanceId']

    def create_service_configversion(self, config_version, config_path):
        q_code, q_data = self._ccs.Describe_ConfigVersion()
        #log.info("Online config Verison: %s" % q_data)

        is_config_version = False
        for v in q_data['versionInfos']:
            if v['version'] == config_version:
                is_config_version = True

        if is_config_version:
            # ConfigVersion already existed
            ## log.info("ConfigVersion %s already existed; No configVersion going to create." % config_version)
            return 0
        else:
            # create new configVersion
            log.info('create new configVersion:  %s' % config_version)

            with codecs.open(config_path, mode='r', encoding='utf-8') as p:
                #config_json = { self._config_name : p.read() }
                #config_yaml = yaml.dump(config_json, default_flow_style=False)

                config_yaml = yaml.dump(yaml.load(p), default_flow_style=False)

            c_code, c_desc = self._ccs.CreateConfigVersion(config_version, config_yaml)

            if not c_code == 0:
                raise ServiceConfigureException("create new service configVerion failed: %s" % c_desc)

        return c_code

    def modify_cluster_service(self, config_version=None, config_path=None, container_name=None, image_tag=None, envlist=None, replicas=None,):
        # get default values with runing service
        log.info('Check cluster service info ...')
        code, describe_data = self._ccs.describe_cluster_service_info()
        if code != 0:
            raise DescribeClusterServiceInfoException("service info err: %s" % describe_data['message'])

        # update config or not
        if config_path is not None and config_version is not None:
            ## get crc value of app config file from cmdb
            import binascii
            with open(config_path, 'rb') as f:
                cmdb_crc = binascii.crc32(f.read())

            #log.info("cmdb crc: %s", cmdb_crc)

            ## get crc value of online configVersion from qcloud ccs
            for v in describe_data['volumes']:
                if v['volumeType'] == 'configMap' and v['configId'] == self._config_id:
                    online_config_version = v['configVersion']

                    online_crc = online_config_version.split('-')[-1]

                    #log.info("online crc: %s" % online_crc)
                    if cmdb_crc != online_crc:
                        new_config_version = self._service_name + '-' + config_version + '-' + str(cmdb_crc)
                        self.create_service_configversion(new_config_version, config_path)

                        ## update service with new config version
                        v['configVersion'] = new_config_version

        # update service with new image tag
        if image_tag is not None:
            for runc in describe_data['containers']:
                #import json
                #log.info(json.dumps(runc, indent=2, ensure_ascii=False))
                #log.info("image: %s - %s" % (runc['image'], image_tag))
                if runc['containerName'] == container_name:
                    new_image = runc['image'].split(':')[0] + ':' + image_tag
                    if runc['image'] != new_image:
                        log.info('modify service with new image tag : %s ' % image_tag)
                        runc['image'] = new_image

        # append or update envs for container
        if envlist is not None and type(envlist) is list:
            for rune in describe_data['containers']:
                if rune['containerName'] == container_name:
                    #log.info(rune['envs'])
                    #log.info(envlist)

                    envs = rune['envs']
                    if envs is None:
                        envs = []

                    # append or add new env to describe_data
                    for new_env in envlist:
                        exist_envvar = False

                        for orig_env in envs:
                            if orig_env['name'] == new_env['name']:
                                if orig_env['value'] != new_env['value']:
                                    orig_env['value'] = new_env['value']
                                    log.info("Update env with new value - { %s: %s }" % (new_env['name'], new_env['value']))
                                exist_envvar = True

                        if not exist_envvar:
                            envs.append(new_env)
                            log.info("Add new env - { %s: %s }" % (new_env['name'], new_env['value']))
                    #log.info(rune['envs'])


        # reset desired number of replicas
        if replicas is not None:
            if int(replicas) == describe_data['desiredReplicas']:
                pass
            else:
                log.info('scale service replicas to %s' % replicas)
                describe_data['desiredReplicas'] = replicas

        # modify service
        m_code, m_data = self._ccs.modify_cluster_service(describe_data)
        if m_code != 0:
            raise ModifyClusterServiceException('modify cluster service error: %s' % m_data['message'])

    def delete_instance(self, instance_id):
        log.info('--//delete instance: %s' % instance_id)
        code, delete_data = self._ccs.delete_cluster_instance(instance_id)
        if code != 0:
            raise DeleteClusterInstanceException("delete instance error: %s" % delete_data['message'])

        ret = False
        if 'requestId' in delete_data:
            log.info('--//wait delete instance(%s) task(%s) .......' % (instance_id, delete_data['requestId']))
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.wait_task_complete(delete_data['requestId']))
            log.info('--// delete instance(%s) task done.' % instance_id)
            ret = True

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.describe_cluster_instance_clean())

        return ret

    def restart_service(self):
        self.stop_service()
        time.sleep(5)
        self.start_service()

    def start_service(self):
        log.info('start service....')
        i_code, d_data = self._ccs.modify_service_replicas(1)
        if i_code != 0:
            raise ModifyServiceReplicasException("modify service err: %s" % d_data['message'])

    def stop_service(self):
        log.info('check cluster service info ...')
        code, describe_data = self._ccs.describe_cluster_service_info()
        if code != 0:
            raise DescribeClusterServiceInfoException("service info err: %s" % describe_data['message'])

        if 'status' in describe_data:
            log.info('modify service instance: 0, stop service...')
            i_code, d_data = self._ccs.modify_service_replicas(0)
            if i_code != 0:
                raise ModifyServiceReplicasException("modify service err: %s" % d_data['message'])

    @asyncio.coroutine
    def describe_service(self):

        container_id = None

        while True:
            yield from asyncio.sleep(10)

            s_code, s_data = self._ccs.describe_cluster_service_info()
            if s_code != 0:
                log.error('describe cluster service info error: %s' % s_data['message'])
                continue

            if 'status' in s_data:
                log.info('service(%s) status: %s..............' % (s_data['serviceName'], s_data['status']))
                if s_data['status'] == 'Abnormal':
                    break
                if s_data['status'] in ['Waiting']:
                    continue

            d_code, d_data = self._ccs.describe_service_instance()
            if d_code != 0:
                log.error('service instance error: %s' % d_data['message'])
                continue

            if 'totalCount' in d_data and d_data['totalCount'] == 0:
                log.warning("service(%s) no exist container." % s_data['serviceName'])
                break

            if 'status' in d_data:
                if d_data['status'] == 'Running':
                    log.info("service(%s) run container(%s)........" % (s_data['serviceName'], d_data['containerId']))

                    if container_id is None:
                        container_id = d_data['containerId']
                    elif container_id == d_data['containerId']:
                        continue
                    else:
                        break
                if d_data['status'] == 'Terminated':
                    log.info('service(%s) container stop' % s_data['serviceName'])
                    break

    def sync_wait_service_terminated(self):

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.describe_service())

    def describe_cluster_service_info(self):

        log.info("check cluster service status ... ")
        ret_code, ret_data = self._ccs.describe_cluster_service_info()
        if ret_code == 0:
            import json
            print(json.dumps(ret_data, indent=2, ensure_ascii=False))

        return ret_code, ret_data

