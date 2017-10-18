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
The playbook creates a new VM (unless an existing one is found),
it runs all the image preparation roles, it creates a new snapshot
and if successful it deletes old snapshots.

It uses existing ansible roles from openstack-infra/devstack-gate.

Limitations:

- only tested on Ubuntu 16.04 OVH image

Dependencies:

- ansible and shade installed

  `pip install -r ansible/requirements.txt`

  - When using a virtual environment, configure the path to python
    in `host_vars/localhost`

- an os-cloud-config style configuration

  - The default profile is called workshop. To use a different one
    configure it in `host_vars/localhost`

- an ssh key in the cloud and on disk

  - The path to the ssh key can be set via an env variable
    WORKSHOP_SSH_KEY or in `group_vars/cloud`

  - The name of the ssh key in the cloud can be set in
    `host_vars/localhost`

To execute the playbook, once the dependencies above are fullfilled,
run the following steps::

  git clone https://git.openstack.org/openstack-infra/devstack-gate
  export ANSIBLE_ROLES_PATH=$PWD/devstack-gate/playbooks/roles:$PWD/devstack-gate/roles
  cd ansible
  ansible-playbook -i inventory setup_image.yaml
