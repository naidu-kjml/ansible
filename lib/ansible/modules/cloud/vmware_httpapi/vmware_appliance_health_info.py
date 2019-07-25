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
module: vmware_appliance_health_info
short_description: Gathers info about health of the VCSA.
description:
- This module can be used to gather information about VCSA health.
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
  attribute:
    description:
    - A subsystem of the VCSA.
    - Valid choices are applmgmt, databasestorage, lastcheck, load, mem, overview, softwarepackages, storage, swap, system
    required: false
    type: str
  asset:
    description:
    - A VCSA asset that has associated health metrics.
    - Valid choices have yet to be determined at this time.
    required: false
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

    - name: Get all health attribute information
      vmware_appliance_health_info:

    - name: Get system health information
      vmware_appliance_health_info:
        attribute: system
'''

RETURN = r'''
attribute:
    description: facts about the specified health attribute
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
        attribute=dict(
            type='str',
            required=False,
            choices=[
                'applmgmt',
                'databasestorage',
                'lastcheck',
                'load',
                'mem',
                'softwarepackages',
                'storage',
                'swap',
                'system',
            ],
        ),
        asset=dict(type='str', required=False),
    )

    module = VmwareRestModule(argument_spec=argument_spec,
                              supports_check_mode=True,
                              is_multipart=True,
                              use_object_handler=True)
    attribute = module.params['attribute']
    asset = module.params['asset']

    slug = dict(
        applmgmt='/health/applmgmt',
        databasestorage='/health/database-storage',
        load='/health/load',
        mem='/health/mem',
        softwarepackages='/health/software-packages',
        storage='/health/storage',
        swap='/health/swap',
        system='/health/system',
        lastcheck='/health/system/lastcheck',
    )

    if asset is not None:
        url = (API['appliance']['base']
                + ('/health/%s/messages' % asset))

        module.submit(url=url, key=asset)
    else:
        if attribute is None:
            attribute = slug.keys()
        for attr in attribute:
            try:
                url = API['appliance']['base'] + slug[attr]
            except KeyError:
                module.fail_json(msg='Please specify correct object type to get '
                                    'information, valid choices are [%s].'
                                    % ", ".join(list(slug.keys())))

            module.submit(url=url, key=attr)

    module.exit()


if __name__ == '__main__':
    main()
