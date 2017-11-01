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
import re

from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils.linux import remote_client
from tempest import test
from testtools import matchers

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
        if not getattr(CONF.service_available, 'neutron', False):
            raise cls.skipException('Neutron support is required')
        if not getattr(CONF.service_available, 'designate', False):
            raise cls.skipException('Designate support is required')
        if not getattr(CONF.service_available, 'heat_plugin', False):
            raise cls.skipException('Heat support is required')

    @classmethod
    def setup_clients(cls):
        super(HeatDriverNeutronDNSIntegration, cls).setup_clients()
        cls.keypair_client = cls.os_primary.compute.KeyPairsClient()
        cls.servers_client = cls.os_primary.compute.ServersClient()
        cls.heat_client = cls.os_primary.orchestration.OrchestrationClient()
        cls.zones_client = cls.os_primary.dns_v2.ZonesClient()
        cls.subnet_client = cls.os_primary.network.SubnetsClient()
        cls.network_client = cls.os_primary.network.NetworksClient()
        cls.network_admin_client = cls.os_admin.network.NetworksClient()
        cls.recordset_client = cls.os_primary.dns_v2.RecordsetClient()

    @classmethod
    def resource_setup(cls):
        super(HeatDriverNeutronDNSIntegration, cls).resource_setup()
        keypair_name = data_utils.rand_name('workshop')
        cls.keypair = cls.keypair_client.create_keypair(
            name=keypair_name)['keypair']
        cls.addClassResourceCleanup(cls.keypair_client.delete_keypair,
                                    keypair_name)

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
            parameters=heat_zone_parameters)['stack']
        zone_stack_id = 'zone/' + zone_stack['id']
        self.addCleanup(self.heat_client.wait_for_stack_status,
                        zone_stack_id, 'DELETE_COMPLETE')
        self.addCleanup(self.heat_client.delete_stack, zone_stack_id)
        self.heat_client.wait_for_stack_status(zone_stack_id,
                                               'CREATE_COMPLETE')
        # There should be only one resources, the zone
        zone_resource = self.heat_client.list_resources(
            zone_stack_id)['resources'][0]

        # Assert that the zone was created and that the ID and name match
        _, zone = self.zones_client.show_zone(
            zone_resource['physical_resource_id'])
        self.assertEqual(CONF.cross_service.dns_domain, zone['name'])

        # Update the private network definition with the domain
        private_network = self.get_tenant_network('primary')
        self.network_client.update_network(
            private_network['id'], dns_domain=CONF.cross_service.dns_domain)
        self.addCleanup(self.network_client.update_network,
                        private_network['id'], dns_domain="")

        # Assert that the network update was successful
        private_network = self.network_client.show_network(
            private_network['id'])['network']
        self.assertEqual(CONF.cross_service.dns_domain,
                         private_network['dns_domain'])

        # Create ports and servers (via HEAT)
        heat_vms_template = load_template(
            __file__, 'servers_in_existing_neutron_net.yaml',
            sub_dir='templates')
        server_name1 = data_utils.rand_name(name='vm1', prefix='workshop')
        server_name2 = data_utils.rand_name(name='vm2', prefix='workshop')
        private_subnet = self.subnet_client.list_subnets(
            network_id=private_network['id'], ip_version=4)['subnets'][0]
        heat_vms_parameters = {
            'server1_name': server_name1,
            'server2_name': server_name2,
            'key_name': self.keypair['name'],
            'image': CONF.compute.image_ref,
            'flavor': CONF.compute.flavor_ref,
            'public_net_id': CONF.network.public_network_id,
            'private_net_id': private_network['id'],
            'private_subnet_id': private_subnet['id']
        }
        vms_stack = self.heat_client.create_stack(
            name='vms', template=heat_vms_template,
            parameters=heat_vms_parameters)['stack']
        vms_stack_id = 'vms/' + vms_stack['id']
        self.addCleanup(self.heat_client.wait_for_stack_status,
                        vms_stack_id, 'DELETE_COMPLETE')
        self.addCleanup(self.heat_client.delete_stack, vms_stack_id)
        self.heat_client.wait_for_stack_status(vms_stack_id,
                                               'CREATE_COMPLETE')
        # Check records have been created
        _, recordsets = self.recordset_client.list_recordset(zone['id'])
        recordsets = recordsets['recordsets']
        # Get all the VM specific records
        recordsets_names = [x['name'] for x in recordsets if
                            x['name'] != CONF.cross_service.dns_domain]
        self.assertEqual(2, len(recordsets_names))
        self.assertIn(server_name1 + "." + CONF.cross_service.dns_domain,
                      recordsets_names)
        self.assertIn(server_name2 + "." + CONF.cross_service.dns_domain,
                      recordsets_names)

        # SSH into a server, resolve other server's name
        vm1 = self.servers_client.list_servers(
            name=server_name1)['servers'][0]
        vm1_public_ip = self.heat_client.show_output(
            vms_stack_id, 'server1_public_ip')
        vm2_private_ip = self.heat_client.show_output(
            vms_stack_id, 'server2_private_ip')
        vm1_ssh = remote_client.RemoteClient(
            vm1_public_ip, CONF.validation.image_ssh_user,
            pkey=self.keypair['private_key'], server=vm1,
            servers_client=self.servers_client)
        # NOTE(andreaf) The following match may be cirros specific
        vm2_lookup = vm1_ssh.exec_command('nslookup %s' % server_name2)
        expected_vm2_lookup = '^Address [0-9]: %s %s.%s$' % (
            vm2_private_ip, server_name2, CONF.cross_service.dns_domain)
        self.assertThat(
            vm2_lookup,
            matchers.MatchesRegex(expected_vm2_lookup, re.MULTILINE))

        # Delete ports and servers (via HEAT)

        # Check records are gone
        pass

    def test_floating_ip_with_own_name_to_dns(self):
        pass
