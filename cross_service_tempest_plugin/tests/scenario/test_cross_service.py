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

import os

from tempest import config
from tempest import test


CONF = config.CONF


def load_template(base_file, file_name, sub_dir=None):
    # NOTE(andreaf) Taken from https://github.com/openstack/heat/blob/master/
    # (...continue) /heat_integrationtests/common/test.py#L161
    sub_dir = sub_dir or ''
    filepath = os.path.join(os.path.dirname(os.path.realpath(base_file)),
                            sub_dir, file_name)
    with open(filepath) as f:
        return f.read()


class HeatDriverNeutronDNSIntegration(test.BaseTestCase):

    credentials = ['primary', 'admin']

    @classmethod
    def skip_checks(cls):
        super(HeatDriverNeutronDNSIntegration, cls).skip_checks()
        if not getattr(CONF.service_available, 'designate', False):
            raise cls.skipException('Designate support is required')
        if not getattr(CONF.service_available, 'heat_plugin', False):
            raise cls.skipException('Heat support is required')

    @classmethod
    def setup_clients(cls):
        super(HeatDriverNeutronDNSIntegration, cls).setup_clients()
        cls.heat_client = cls.os_primary.orchestration.OrchestrationClient()
        cls.zones_client = cls.os_primary.dns_v2.ZonesClient()
        cls.network_admin_client = cls.os_admin.network.NetworksClient()
        cls.records_client = cls.os_primary.dns_v2.RecordsetClient()

    def test_port_on_extenal_net_to_dns(self):
        pass

    def test_floating_ip_with_name_from_port_to_dns(self):
        heat_zone_template = load_template(
            __file__, 'designate_domain.yaml', sub_dir='templates')
        heat_zone_parameters = {
            'name': CONF.cross_service.dns_domain,
            'email': 'sydney-workshop@my-openstack.org',
            'ttl': 120,
            'description': 'test_floating_ip_with_name_from_port_to_dns'
        }
        # Create the domain on designate (via HEAT)
        zone_stack = self.heat_client.create_stack(
            name='zone', template=heat_zone_template,
            parameters=heat_zone_parameters)
        zone_stack_id = zone_stack['name'] + '/' + zone_stack['id']
        self.addCleanup(self.heat_client.wait_for_stack_status,
                        zone_stack_id, 'DELETE_COMPLETE')
        self.addCleanup(self.heat_client.delete_stack, zone_stack_id)
        self.heat_client.wait_for_stack_status(zone_stack_id,
                                               'CREATE_COMPLETE')
        # There should be only one resources, the zone
        zone_resource = next(self.heat_client.list_resources(
            zone_stack_id)['resources'])

        # Assert that the zone was created and that the ID and name match
        zone = self.zones_client.show_zone(
            zone_resource['physical_resource_id'])
        self.assertEqual(CONF.cross_service.dns_domain, zone['name'])

        # Update the public network definition with the domain

        # Create ports and servers (via HEAT)

        # Check records have been created

        # SSH into a server, resolve other server's name

        # Delete ports and servers (via HEAT)

        # Check records are gone
        pass

    def test_floating_ip_with_own_name_to_dns(self):
        pass
