# Copyright 2017 Andrea Frittoli
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest import config
from tempest import test


CONF = config.CONF


class HeatDriverNeutronDNSIntegration(test.BaseTestCase):

    @classmethod
    def skip_checks(cls):
        super(HeatDriverNeutronDNSIntegration, cls).skip_checks()
        if not getattr(CONF.service_available, 'dns', False):
            raise cls.skipException('Designate support is required')
        if not getattr(CONF.service_available, 'orchestration', False):
            raise cls.skipException('Heat support is required')

    def test_port_on_extenal_net_to_dns(self):
        pass

    def test_floating_ip_with_name_from_port_to_dns(self):
        pass

    def test_floating_ip_with_own_name_to_dns(self):
        pass
