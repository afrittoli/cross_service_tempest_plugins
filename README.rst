Writing cross-service Tempest plugins - Hands-on
================================================

This repo contains the code and documentation for the Hands-on Workshop
"Writing cross-service Tempest Plugins".

Introduction
------------

To run through the workshop preparation steps:
- building the workshop image
- snapshot it to build a ready-image for students

To run through the workshop itself:
- spawn a VM using the built image
- follow the steps from the README

Building the Workshop Image
---------------------------

The image setup is done via the setup_image.yaml playbook.
It uses existing ansible roles from openstack-infra/devstack-gate.

To run the playbook, define the IP of your cloud VM and the
passwordless user to connect to it in the `inventory` file.
The run the following steps::

  git clone https://git.openstack.org/openstack-infra/devstack-gate
  export ANSIBLE_ROLES_PATH=$PWD/devstack-gate/playbooks/roles
  ansible-playbook setup_image.yaml
