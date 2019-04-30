#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2015, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: vsphere_copy
short_description: Copy a file to a VMware datastore
description:
    - Upload files to a VMware datastore through a VCenter of a ESXi
version_added: 2.0
author:
- Dag Wieers (@dagwieers)
options:
  hostname:
    version_added: "2.9"
  port:
    version_added: "2.9"
  username:
    version_added: "2.9"
  host:
    description:
      - (description) Use C(hostname) instead like the other VMware modules
      - The vCenter or ESXi server on which the datastore is available.
      - This option is deprecated and will eventually be removed in 2.12.
    aliases: ['hostname']
  login:
    description:
      - (description) Use C(username) instead like the other VMware modules
      - The login name to authenticate on the vCenter or ESXi server.
      - This option is deprecated and will eventually be removed in 2.12.
    aliases: ['username']
  src:
    description:
      - The file to push to vCenter
    required: true
  datacenter:
    description:
      - The datacenter on the vCenter server that holds the datastore.
    required: false
  datastore:
    description:
      - The datastore to push files to.
    required: false
  path:
    description:
      - The file to push to the datastore.
    required: true
  timeout:
    description:
      - The timeout in seconds for the upload to the datastore.
    default: 10
    type: int
    version_added: "2.8"

notes:
  - "This module ought to be run from a system that can access the vCenter or the ESXi directly and has the file to transfer.
    It can be the normal remote target or you can change it either by using C(transport: local) or using C(delegate_to)."
  - Tested on vSphere 5.5 and ESXi 6.7
extends_documentation_fragment: vmware.documentation
'''

EXAMPLES = '''
- vsphere_copy:
    host: '{{ vhost }}'
    login: '{{ vuser }}'
    password: '{{ vpass }}'
    src: /some/local/file
    datacenter: DC1 Someplace
    datastore: datastore1
    path: some/remote/file
  delegate_to: localhost

- vsphere_copy:
    host: '{{ vhost }}'
    login: '{{ vuser }}'
    password: '{{ vpass }}'
    src: /other/local/file
    datacenter: DC2 Someplace
    datastore: datastore2
    path: other/remote/file
  delegate_to: other_system
'''

import atexit
import errno
import mmap
import socket
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote
from ansible.module_utils._text import to_native
from ansible.module_utils.urls import open_url
from ansible.module_utils.vmware import connect_to_api, vmware_argument_spec


def vmware_path(datastore, datacenter, path):
    ''' Constructs a URL path that VSphere accepts reliably '''
    path = "/folder/%s" % quote(path.lstrip("/"))
    # Due to a software bug in vSphere, it fails to handle ampersand in datacenter names
    # The solution is to do what vSphere does (when browsing) and double-encode ampersands, maybe others ?
    if not path.startswith("/"):
        path = "/" + path
    params = dict(dsName=datastore)
    if datacenter:
        datacenter = datacenter.replace('&', '%26')
        params["dcPath"] = datacenter
    params = urlencode(params)
    return "%s?%s" % (path, params)


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(dict(
        host=dict(required=False),
        login=dict(required=False),
        src=dict(required=True, aliases=['name']),
        datacenter=dict(required=False),
        datastore=dict(required=True),
        dest=dict(required=True, aliases=['path']),
        timeout=dict(default=10, type='int')
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        # Implementing check-mode using HEAD is impossible, since size/date is not 100% reliable
        supports_check_mode=False,
    )

    if module.params['host'] is not None:
        module.deprecate("The 'host' option is being replaced by 'hostname'", version='2.12')
    if module.params['login'] is not None:
        module.deprecate("The 'login' option is being replaced by 'username'", version='2.12')

    hostname = module.params['host'] or module.params['hostname']
    username = module.params['login'] or module.params['username']
    password = module.params.get('password')
    src = module.params.get('src')
    datacenter = module.params.get('datacenter')
    datastore = module.params.get('datastore')
    dest = module.params.get('dest')
    validate_certs = module.params.get('validate_certs')
    timeout = module.params.get('timeout')

    fd = open(src, "rb")
    atexit.register(fd.close)

    data = mmap.mmap(fd.fileno(), 0, access=mmap.ACCESS_READ)
    atexit.register(data.close)

    remote_path = vmware_path(datastore, datacenter, dest)
    url = 'https://%s%s' % (hostname, remote_path)

    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Length": str(len(data)),
    }

    try:
        r = open_url(url, data=data, headers=headers, method='PUT', timeout=timeout,
                     url_username=username, url_password=password, validate_certs=validate_certs,
                     force_basic_auth=True)
    except socket.error as e:
        if isinstance(e.args, tuple) and e[0] == errno.ECONNRESET:
            # VSphere resets connection if the file is in use and cannot be replaced
            module.fail_json(msg='Failed to upload, image probably in use', status=None, errno=e[0], reason=to_native(e), url=url)
        else:
            module.fail_json(msg=str(e), status=None, errno=e[0], reason=str(e),
                             url=url, exception=traceback.format_exc())
    except Exception as e:
        error_code = -1
        try:
            if isinstance(e[0], int):
                error_code = e[0]
        except KeyError:
            pass
        module.fail_json(msg=to_native(e), status=None, errno=error_code,
                         reason=to_native(e), url=url, exception=traceback.format_exc())

    status = r.getcode()
    if 200 <= status < 300:
        module.exit_json(changed=True, status=status, reason=r.msg, url=url)
    else:
        length = r.headers.get('content-length', None)
        if r.headers.get('transfer-encoding', '').lower() == 'chunked':
            chunked = 1
        else:
            chunked = 0

        module.fail_json(msg='Failed to upload', errno=None, status=status, reason=r.msg, length=length, headers=dict(r.headers), chunked=chunked, url=url)


if __name__ == '__main__':
    main()
