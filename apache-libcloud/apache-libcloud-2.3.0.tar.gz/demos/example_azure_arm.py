# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import libcloud.security
libcloud.security.VERIFY_SSL_CERT = False

subscription_id = "35867a13-9915-428e-a146-97f3039bba98"
key = '8038bf1e-2ccc-4103-8d0c-03cabdb6319c'
secret = 'wrapAtH6!'


cls = get_driver(Provider.AZURE_ARM)
driver = cls(tenant_id='e3cf3c98-a978-465f-8254-9d541eeea73c',
             subscription_id=subscription_id,
             http_proxy='http://localhost:8888',
             key=key, secret=secret,
             region='eastus')

# nodes = driver.list_nodes()
# print(nodes)
# # nodes[0].reboot()
# print(driver.list_locations())
# driver.ex_get_ratecard('0026P')
# publishers = driver.ex_list_publishers()
# offers = driver.ex_list_offers(publishers[0][0])
# skus = driver.ex_list_skus(offers[0][0])
# image_versions = driver.ex_list_image_versions(skus[0])

resource_groups = driver.ex_list_resource_groups()
networks = driver.ex_list_networks(resource_groups[2])
# ips = driver.ex_list_public_ips(resource_groups[2])
# driver.ex_list_network_security_groups(resource_groups[2].name)

# group = driver.ex_create_network_security_group('example', resource_groups[2].name)

sizes = driver.list_sizes(location=driver.list_locations()[0])