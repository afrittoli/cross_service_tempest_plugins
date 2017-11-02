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

The Designate team already maintains a Tempest plugin. It will require a few
tweaks for our scope.
The Heat team maintains a Tempest plugin in tree; they're working on creating
and out of tree one. I created one for the purpose of this workshop.

A new plugin includes tests specific for this constellation. It depends on
both Designate and Heat plugins as well as Tempest and its stable APIs.

Plugin Skeleton
---------------

Work with the Tempest user::

  sudo -i
  su - tempest

We start by creating the structure of the new plugin::

  pip install cookiecutter
  cookiecutter https://git.openstack.org/openstack/tempest-plugin-cookiecutter.git

Project and repo_name can be "cross_service".  The testclass is
`CrossServiceTempestPlugin`.
