=========================================
Building the cross-service Tempest plugin
=========================================

This document is a walk-through to build a Tempest plugin that uses multiple
other Tempest plugins. 

The whole code of the plugin is available on the test machine or at
_https://github.com/afrittoli/cross_service_tempest_plugins. As long as you
use the proposed projecy and class name you should be able to complement you
work with code from the final plugin at any time.

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
