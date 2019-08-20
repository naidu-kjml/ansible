#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Paul Knight <paul.knight@delaware.gov>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: vmware_appliance_access_info
short_description: Gathers info about modes of access to the vCenter appliance using REST API.
description:
- This module can be used to gather information about the four modes of accessing the VCSA: consolecli, dcui, shell, and ssh.
- This module is based on REST API and uses httpapi connection plugin for persistent connection.
- The Appliance API works against the VCSA and uses the "administrator@vsphere.local" user.
version_added: '2.9'
author:
- Paul Knight (@n3pjk)
notes:
- Tested on vSphere 6.7
requirements:
- python >= 2.6
options:
  access_mode:
    description:
    - Method of access to get to appliance
    - If not specified, all modes will be returned.
    required: false
    choices: ['consolecli', 'dcui', 'shell', 'ssh']
    type: str
'''

EXAMPLES = r'''
- hosts: all
  connection: httpapi
  gather_facts: false
  vars:
    ansible_network_os: vmware
    ansible_host: vcenter.my.domain
    ansible_user: administrator@vsphere.local
    ansible_httpapi_password: "SomePassword"
    ansbile_httpapi_use_ssl: yes
    ansible_httpapi_validate_certs: false
  tasks:

  - name: Get all access modes information
    vmware_appliance_access_info:

  - name: Get ssh access mode information
    vmware_appliance_access_info:
      access_mode: ssh
'''

RETURN = r'''
access_mode:
    description: facts about the specified access mode
    returned: always
    type: dict
    sample: {
        "value": true
    }
'''

from ansible.module_utils.vmware.VmwareRestModule import API, VmwareRestModule


def main():
    argument_spec = VmwareRestModule.rest_argument_spec()
    argument_spec.update(
        access_mode=dict(type='str', choices=['consolecli', 'dcui', 'shell', 'ssh'], default=None),
    )

    module = VmwareRestModule(argument_spec=argument_spec,
                              supports_check_mode=True,
                              is_multipart=True,
                              use_object_handler=True)
    access_mode = module.params['access_mode']

    slug = dict(
        consolecli='/access/consolecli',
        dcui='/access/dcui',
        shell='/access/shell',
        ssh='/access/ssh',
    )

    if access_mode:
        access_mode = [access_mode]
    else:
        access_mode = slug.keys()

    for mode in access_mode:
        try:
            url = API['appliance']['base'] + slug[mode]
        except KeyError:
            module.fail_json(msg='Please specify correct object type to get '
                             'information, valid choices are [%s].' % ", ".join(list(slug.keys())))

        module.submit(url=url, key=mode)

    module.exit()


if __name__ == '__main__':
    main()
