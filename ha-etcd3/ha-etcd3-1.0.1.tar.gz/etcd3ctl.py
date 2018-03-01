#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-02-26
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


import etcd3
import time
import _thread
import urllib
import traceback
import os
import signal

ELECTION_TIMEOUT = 0.500


class Client(object):
    """
    ETCD client for ha
    """
    def __init__(self, namespace, on_resume=None, on_pause=None, ttl=3, timeout=1, urls=("localhost:2379",)):
        if urls is None or len(urls) == 0:
            raise Exception("'urls' cannot be empty")
        self.namespace = namespace
        self.ttl = ttl
        self.timeout = timeout
        self.heartbeat_time = self.ttl / 3
        self.urls = urls
        self.etcd_client = None
        self.on_resume = on_resume
        self.on_pause = on_pause

    def setup_etcd_server(self):
        time.sleep(ELECTION_TIMEOUT)
        for url in self.urls:
            host, port = url.split(":")
            client = etcd3.client(host=host, port=port, timeout=self.timeout)
            try:
                status = client.status()
            except Exception as e:
                continue
            if status.leader is None:
                continue
            leader_urls = status.leader.client_urls
            if len(leader_urls) == 1:
                leader_url = leader_urls[0]
                host, port = urllib.parse.urlsplit(leader_url).netloc.split(":")
                self.etcd_client = etcd3.client(host=host, port=port, timeout=self.timeout)
                return
        raise Exception("All etcd servers are unavailable")

    def register_service(self, service_url):
        with self.etcd_client.lock(self.namespace) as lock:
            ret = self.etcd_client.get(self.namespace)
            if type(ret) == tuple and ret[0] is None:
                self._start_heartbeat(service_url)
                return True
        return False

    def _start_heartbeat(self, service_url):
        lease = self.etcd_client.lease(self.ttl)
        self.etcd_client.put(self.namespace, service_url, lease)
        _thread.start_new_thread(self._refresh_lease, (lease.id,))

    def _refresh_lease(self, lease_id):
        while True:
            time.sleep(self.heartbeat_time)
            try:
                try:
                    list(self.etcd_client.refresh_lease(lease_id))
                except etcd3.exceptions.ConnectionFailedError as e:
                    time.sleep(ELECTION_TIMEOUT)
                    self.setup_etcd_server()
            except:
                os.kill(os.getpid(), signal.SIGKILL)

    def watch_callback(self):
        try:
            iterator, cancel = self.etcd_client.watch(self.namespace)
            for event in iterator:
                if self.on_resume and isinstance(event, etcd3.events.PutEvent):
                    self.on_resume()
                elif self.on_pause and isinstance(event, etcd3.events.DeleteEvent):
                    self.on_pause()
        except etcd3.exceptions.ConnectionFailedError as e:
            self.setup_etcd_server()
            self.watch_callback()
        except:
            raise

    def get_current_service_url(self):
        try:
            ret = self.etcd_client.get(self.namespace)
        except:
            self.setup_etcd_server()
            ret = self.etcd_client.get(self.namespace)
        if ret and type(ret) == tuple:
            return ret[0].decode("utf-8")

