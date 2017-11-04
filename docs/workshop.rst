=========================================
Building the cross-service Tempest plugin
=========================================

This document is a walk-through to build a Tempest plugin that uses multiple
other Tempest plugins. 

The whole code of the plugin is available on the test machine or at
_https://github.com/afrittoli/cross_service_tempest_plugins. As long as you
use the proposed projecy and class name you should be able to complement you
work with code from the final plugin at any time.

Scenario Description
--------------------

Let's say we define a constellation which includes DNS services integrated
with Neutron and Nova, provided by Designate, and orchestration services
provided by Heat.

Nova, Neutron and Designate integration is well documented at:
https://docs.openstack.org/neutron/latest/admin/config-dns-int.html#use-case-2-floating-ips-are-published-with-associated-port-dns-attributes.
The scenarios are rather simple - we want to boot VMs and have DNS records
automatically associated with them. The docs do not use Heat to achieve that,
but we can easily map operations from the docs into Heat templates.

The Solution
------------

We would like to automate those scenarios using the Tempest test suite. The
tests will possibly run in a constellation dedicated periodic job, which
ensures integration between the above services is working fine.

Tempest interacts with services via API, using Tempest own service clients.
Tempest exposes a plugin interfaces, which allows bunlding a set of
configuration items, service clients and tests in a python package.
*TBD Link to Tempest plugin spec*

The Designate team already maintains a Tempest plugin. It will require a few
tweaks for our scope.
The Heat team maintains a Tempest plugin in tree; they're working on creating
and out of tree one. I created one for the purpose of this workshop.

A new plugin includes tests specific for this constellation. It depends on
both Designate and Heat plugins as well as Tempest and its stable APIs.

The SUT
-------

The development and test environemnt is a devstack based cloud. The custom
image used to run the devstack cloud contains a `stack` linux account, with
a set password. The OpenStack version is Pike. At the time of writing Queens
is under development and we need a stable environment for the workshop.

Devstack by default provisions three OpenStack accounts. Two are regular
users and one is an admin user. Two use these accounts wih the `openstack`
client, export OS_CLOUD accordingly.

Let's check which services are available::

  export OS_CLOUD=devstack
  openstack service list
  openstack endpoint list

We will need one image to boot servers. A CirrOS image has been provisioned
during the cloud setup process::

  openstack image list

This devstack instance has been pre-configured for the purpose of this
workshop. Let's have a look at the configuration changes we made::

  less ~/devstack/local.conf

There are a number of changes. The most interesting ones are:

* Disable Horizon and Swift to save resources, since we don't need them
* Enable heat and designate by loading the corresponding devstack plugin
* Configure the DNS driver and DNS domain in Neutron
* Set Designate specific settings in Neutron

When we run stack.sh configuration settings are propagated into service
configuration files as well as test configuration files (where relevant).
The devstack plugin interface defines a test-config (*Check*) interface
that can be used to configure the corresponding plugin or even core
Tempest settings.

Let's change the DNS domain to a name of your liking. We cannot do that
in `local.conf` since that would require us to unstack and stack again,
which will take 20m+. But we can edit Neutron configuration directly
and restart services::

  vim /etc/neutron/neutron.conf
  # Set dns_domain. The new domain must end with a '.'
  # Save and close. Restart all neutron services
  sudo systemctl restart devstack@q-*

From now on I will refer to the domain name you defined as $DOMAIN_NAME.
To check the status of a service, you can::

  sudo systemctl status devstack@q-svc

To check logs, use journactl. `-a` for all logs, `-f` to tail::

  sudo journalctl [-a|-f] --unit devstack@q-*

*TBD link to devstak docs on systemd*


Tempest setup
-------------

Tempest is pre-configured by devstack. The configuration file is available
at `~/tempest/etc/tempest.conf`. A virtual environemnt for Tempest is
pre-installed at `~/tempest/.tox/tempest`. Since Tempest is branchless, its
dependencies may conflict with devstack Pike, so Tempest must be installed
in a virtual environment.

Tempest log can be found at `~/tempest/tempest.log`.


Workshop material
-----------------

Everything you need to run through the workshop is available under
`~/workshop`. You can copy code from there or write your own.

All material is publicicly available on github, under the Apache 2.0 license.
The cross-service-tempest-plugin repo includes the ansible play that I used
to prepare the SUT image. You can easily recreate it and customise it on any
OpenStack cloud.

Pull requests are welcome:

* https://github.com/afrittoli/designate-tempest-plugin
* https://github.com/afrittoli/heat-tempest-plugin
* https://github.com/afrittoli/cross-service-tempest-plugin


Manual scenario run
-------------------
*TBD*


Run as a Tempest test
---------------------

Plugin Skeleton
'''''''''''''''

We start by creating the structure of the new plugin::

  cd ~
  pip install cookiecutter
  cookiecutter https://git.openstack.org/openstack/tempest-plugin-cookiecutter.git

Project and repo_name can be "cross_service".  The testclass is
`CrossServiceTempestPlugin`.


Make the plugin installable
'''''''''''''''''''''''''''

Like most OpenStack projects we use pbr to simplify our setup.py.
We need three files, which we can copy from ~/workshop/cross_service_tempest_plugin/

* setup.cfg
* setup.py
* requirements.txt

Check the installation process::

  . ~/tempest/.tox/tempest/bin/activate
  pip install -e ~/cross_service_tempest_plugin


Make the plugin configurable
''''''''''''''''''''''''''''

Since we customised the DNS domain name, we'll need a way to tell our test what domain
name to use. Tempest plugins allow extending the standard Tempest configuration file
with plugin custom configuration groups and values.

File we need to add / edit:

* cross_service_tempest_plugin/config.py
* cross_service_tempest_plugin/plugin.py

In config.py we can leave the default value as is, we'll set the proper configuration
later in tempest.conf::

      cfg.StrOpt('dns_domain',
               default='my-workshop-domain.org.',
               help="The DNS domain used for testing."),

In plugin.py we need to implement two interfaces:

* `register_opts` is used by Tempest to register the extra options
* `get_opt_lists` is used for config option discovery, used for instance to generate
  a sample config file


Implement the service client interface
''''''''''''''''''''''''''''''''''''''

We already have all the service clients we need from either Tempest or other plugins,
we don't need to define any new one::

    def get_service_clients(self):
        # No extra service client defined by this plugin
        return []


Create a test module and make it discoverable
'''''''''''''''''''''''''''''''''''''''''''''

Add a test module in `~/cross_service_tempest_plugin/cross_service_tempest_plugin/tests/scenario`.
I called mine `test_cross_service.py`. We'll only need the class definition and
a test method.  The test method name must start with `test_` for discovery to
find it::

  from tempest import test

  class HeatDriverNeutronDNSIntegration(test.BaseTestCase):
    
      def test_floating_ip_with_name_from_port_to_dns(self):
        pass


Let's test it::

  pip install -e ~/cross_service_tempest_plugin
  cd ~/tempest
  tempest run --regex test_cross_service --list
  tempest run --regex test_cross_service

*Do I really need to re-install?*

Phases in Tempest test.py class setup
'''''''''''''''''''''''''''''''''''''

*TBD Add link to docs*

* `skip_checks`
* `setup_credentials`
* `setup_clients`
* `resource_setup`

Setup skip rules
''''''''''''''''

The `service_available` configuration options group let us selectively run
tests depending on the set of services available in the cloud under test.
Plugin specific to a service usually add one entry in this group to allow
for tests to be skipped automatically if a service is not available.

The test that we're about to write depends on Keystone, Nova, Neutron,
Designate and Heat. We assume Keystone is there since without Keystone no
Tempest test would work.

We can implement `skip_checks` as follows::

    @classmethod
    def skip_checks(cls):
        super(HeatDriverNeutronDNSIntegration, cls).skip_checks()
        if not getattr(CONF.service_available, 'neutron', False):
            raise cls.skipException('Neutron support is required')
        if not getattr(CONF.service_available, 'nova', False):
            raise cls.skipException('Nova support is required')
        if not getattr(CONF.service_available, 'designate', False):
            raise cls.skipException('Designate support is required')
        if not getattr(CONF.service_available, 'heat_plugin', False):
            raise cls.skipException('Heat support is required')

To test this is working, we can uninstall one of the plugins we depend on::

  pip unsintall heat_tempest_plugin
  cd ~/tempest
  tempest run --regex test_cross_service

And then we reinstall the plugin again::

  pip install -e ~/workshop/heat_tempest_plugin
  cd ~/tempest
  tempest run --regex test_cross_service


Setup credentials
'''''''''''''''''

The logic to provision and de-provision test credentials is handled
automatically by the the base test class `test.py`. The only thing we need to
do is define which credentials we need to be provisioned for us. They will be
created as part of `setup_credentials` along with network resources. The only
time a test needs to overwrite `setup_credentials` is if it needs to disable
provisioning of network resources. *TBD link to docs*.  This is not the case
for us, so we only need::

  class HeatDriverNeutronDNSIntegration(test.BaseTestCase):
            
      credentials = ['primary', 'admin']


Setup client aliases
''''''''''''''''''''

This step is, strictly speaking, not required. Creating aliases for clients can
be convenient though since it makes the code simpler and more readable. This
can be a double-edged sword: if a test relies on aliases setup by a parent test
class, it can become difficult to know what client alias does what, which may
lead to hard to debug issues.  *TBD link to docs**

Tempest base classes sets up a `ServiceClient` object for each type of
credentials that has been requested. They can be accessed via
`cls.os_<cred_type>`. `ServiceClient` objects provide access to service clients
initialised with a set of credentials and with parameters from CONF.
`ServiceClient` is dynamically extended with extra service clients for each
plugin that implements the `get_service_clients` interface, as detailed in
*TBD link to docs for this*.

To show how this works, let's have a look at the `get_service_client`
implementation in the Heat and Designate Tempest plugins. *TBD links*. We can
obtain an instance of any client defined in the parameters returned by the
plugin by simply invoking it. All the parameters from configuration and the
credentials are pre-fed into clients.

For example::

      cls.heat_client = cls.os_primary.orchestration.OrchestrationClient()
      cls.zones_client = cls.os_primary.dns_v2.ZonesClient()
      cls.network_admin_client = cls.os_admin.network.NetworksClient()
      cls.recordset_admin_client = cls.os_admin.dns_v2.RecordsetClient()


Resource Setup
''''''''''''''

A test class can include several tests. Resources that takes time to provision
and that can be safeily re-used by multiple tests can be provisioned here. 
Tempest test base class provides a `addClassResourceCleanup` helper that should
be used in this case to schedule the cleanup of resources.

In the case of our tests, we could setup the DMS zone ones and re-use it for
multiple tests. However is a test failed to cleanup recordsets properly, it
would have an impact on other tests. Deleting the zone after each test may
help a bit, even though the DNS domain is inherently not multi-tenant, so
we cannot completely avoid the risk of a test failure having an impact on other
tests.

To demonstrate how to use `resource_setup` we provision a keypair, which we
can safely re-use in multiple tests to boot servers::

    @classmethod
    def resource_setup(cls):
        super(HeatDriverNeutronDNSIntegration, cls).resource_setup()
        keypair_name = data_utils.rand_name('workshop')
        cls.keypair = cls.keypair_client.create_keypair(
            name=keypair_name)['keypair']
        cls.addClassResourceCleanup(test_utils.call_and_ignore_notfound_exc,
                                    cls.keypair_client.delete_keypair,
                                    keypair_name)

Heat Templates
''''''''''''''

We will define two stacks:

* the first creates the DNS zone
* the second one creates ports, VMs, floating IPs and security groups

We don't have to start from scratch. There are templates available from the
Heat team that we can re-use with minimal modifications:

- *TBD links to thw two templates we used*

It's useful to add resource names as inputs to the stacks since that allows
to provision resources that can be associated with their tests when debugging.

We store our customised templates under `tests/scenario/templates`, and we
borrow a small helper from the Heat tests to load templates *TDB link*.


Writing the Test
''''''''''''''''

We now have everything we need to write the scenario as a Tempest test.
Steps of the tests are:

* Create the domain in designate (via HEAT)
* Assert the zone was created correctly
* Update the private network definition with the domain
* Assert that the network update was successful
* Create ports and servers stack (via HEAT)
* Check records have been created
* Check PTR records have been created
* Ssh into a server, resolve the other server's name
* Delete the ports and servers stack (via HEAT)
* Check recordsets are deleted
* Check PTR recordsets are deleted

Depending on time, we can analyse each step in more details.
Test intermediate states of your test code by running it::

  tempest run --regex test_cross_service


Best practices
''''''''''''''

- Name resources so that they be easily identified in logs
- Schedule cleanup right after creation
- Use `test_utils.call_and_ignore_notfound_exc` when invoking a delete method
- Wait for status when create / delete / API action is not synchronous
- Use assert in a way that it gives useful info when failing. For instance
  `assertSetEqual` and `assertDictEqual` test all fields and report all
  differences in a nice format - often useful on API tests
- When writing tests for the gate, mind the test time!
- Avoid race conditions, never test for transient states
- For scenario tests, use log statements to help find your bearing in the log
  while debugging


Tips & Tricks
'''''''''''''

By default Tempest creates dynamic test credentials that are deleted at the
end of the test run. That is helpful for test isolation but it does not
help for test development. You can go around that with a few tricks:
- use pre-provisioned credentials *TBD details*
- prevent cleanup of credentials and of resources by overriding cleanup
  methods
- use print statements and make sure the test fails. Captured stdout will be
  displayed for your test at the end of the run


More Scenarios
--------------

If you have extra time during the workshop, or want to practise after it,
you can implement more test scenarios. There are two more similar scenarios
that can be implemented for this constellation or you can implement a
scenario that is relevant for you.
Feel free to submit pull requsts to my repo, I will be happy to review and
provide feedback, or even merge them in the reop if you want.
Or send me gerrit / github links to your multi-service test if you have
issues you need help with. You can find me on IRC in #openstack-qa as andreaf.
