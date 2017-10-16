Writing cross-service Tempest plugins - Hands-on
================================================

This repo contains the code and documentation for the Hands-on Workshop
"Writing cross-service Tempest Plugins".

Introduction
------------

To run through the workshop preparation steps:
- build the workshop image
- snapshot it to build a ready-image for students

To run through the workshop itself:
- spawn a VM using the built image
- follow the steps from the README

Building the Workshop Image
---------------------------

The image setup is done via the setup_image.yaml playbook.
It uses existing ansible roles from openstack-infra/devstack-gate.

Dependencies:

- only tested on Ubuntu 16.04 OVH image

- ansible and shade installed

  - When using a virtual environment, configure the path to python
    in `host_vars/localhost`

- an os-cloud-config style configuration

  - The default profile is called workshop. To use a different one
    configure it in `host_vars/localhost`

- an ssh key already available in the cloud and on disk

  - The path to the ssh key can be set via an env variable
    WORKSHOP_SSH_KEY or in `group_vars/cloud`

  - The name of the ssh key in the cloud can be set in
    `host_vars/localhost`

To run the playbook, define the IP of your cloud VM and the
passwordless user to connect to it in the `inventory` file.
The run the following steps::

  git clone https://git.openstack.org/openstack-infra/devstack-gate
  export ANSIBLE_ROLES_PATH=$PWD/devstack-gate/playbooks/roles
  ansible-playbook setup_image.yaml
