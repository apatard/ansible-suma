#!/usr/bin/python
# Copyright (c) 2022, Arnaud Patard <apatard@hupstream.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.apatard.suma.plugins.module_utils.suma_utils import (
    suma_connect,
)
from xmlrpc.client import Fault as rpcFault

DOCUMENTATION = """
---
module: system_info
author: "Arnaud Patard"
short_description: Return info about a system registered to SUMA
description:
   - Returns product list of a host
options:
   id:
     description:
        - system id
     required: true
   info:
     description:
        - system infos to return
     required: true
   hostname:
     description:
        - host running the Suse Manager instance.
     required: true
   login:
     description:
        - account on the Suse Manager instance.
     required: true
   password:
     description:
        - password of the suse manager account
     required: true
   ssl_check:
     description:
        - disable SSL check *dangerous*
     required: false
"""


def main():
    module = AnsibleModule(
        argument_spec=dict(
            id=dict(required=True, type="int"),
            info=dict(required=True, choices=["products"]),
            hostname=dict(required=True),
            login=dict(required=True),
            password=dict(required=True, no_log=True),
            ssl_check=dict(required=False, type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    (client, session_key) = suma_connect(module)

    try:
        info = client.system.getInstalledProducts(session_key, module.params["id"])
    except rpcFault as fault:
        client.auth.logout(session_key)
        module.fail_json(msg=f"Failed to get system installed products list: {fault}")

    client.auth.logout(session_key)
    module.exit_json(changed=False, info=info)


if __name__ == "__main__":
    main()
