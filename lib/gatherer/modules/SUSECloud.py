# Copyright (c) 2015 SUSE LLC, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import json
import logging
from novaclient.v1_1 import client

class SUSECloudWorker:
    def __init__(self, node):
        self.log = logging.getLogger(__name__)
        for k in parameter():
            if k not in node:
                self.log.error("Missing parameter '%s' in infile", k)
                raise AttributeError("Missing parameter '%s' in infile" % k)

        self.host = node['host']
        self.port = node['port'] or 5000
        self.user = node['user']
        self.password = node['pass']
        self.tenant = node['tenant']

    def run(self):
        output = dict()
        url = "http://%s:%s/v2.0/" % (self.host, self.port)
        self.log.info("Connect to %s for tenant %s as user %s", url, self.tenant, self.user)
        nt = client.Client(self.user, self.password, self.tenant, url, service_type="compute")
        hypervisors = nt.hypervisors.list()
        for hyp in hypervisors:
            cpu_info = json.loads(hyp.cpu_info)
            output[hyp.hypervisor_hostname] = {'name': hyp.hypervisor_hostname,
                                               'sockets': cpu_info['topology']['sockets'],
                                               'cores': cpu_info['topology']['cores'],
                                               'threads': cpu_info['topology']['threads'],
                                               'ghz': 0,
                                               'ram': hyp.memory_mb,
                                               'vms': {}
                                               }
            reslist = nt.hypervisors.search(hyp.hypervisor_hostname, True)
            for result in reslist:
                if not hasattr(result, 'servers'):
                    continue
                for vm in result.servers:
                    output[hyp.hypervisor_hostname]['vms'][vm['name']] = vm['uuid']

        return output

def parameter():
    return {'host': '',
            'port': 5000,
            'user': '',
            'pass': '',
            'proto': 'https',
            'tenant': 'openstack'}

def worker(node):
    return SUSECloudWorker(node)