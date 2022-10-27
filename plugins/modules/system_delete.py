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
module: system_delete
author: "Arnaud Patard"
short_description: Delete a system from SUMA
description:
   - Delete synchronously a system
options:
   id:
     description:
        - system id
     required: true
   cleanup_type:
     description:
        - Cleanup behaviour
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
            cleanup=dict(required=True, choices=["fail_on_err", "none", "force"]),
            hostname=dict(required=True),
            login=dict(required=True),
            password=dict(required=True, no_log=True),
            ssl_check=dict(required=False, type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    if module.params["cleanup"] == "fail_on_err":
        cleanup = "FAIL_ON_CLEANUP_ERR"
    elif module.params["cleanup"] == "none":
        cleanup = "NO_CLEANUP"
    else:
        cleanup = "FORCE_DELETE"

    (client, session_key) = suma_connect(module)

    try:
        syslist = client.system.listSystems(session_key)
    except rpcFault as fault:
        client.auth.logout(session_key)
        module.fail_json(msg=f"Failed to get list of systems: {fault}")

    try:
        next(sysinfo for sysinfo in syslist if sysinfo["id"] == module.params["id"])
    except StopIteration:
        client.auth.logout(session_key)
        module.exit_json(changed=False)

    try:
        if not module.check_mode:
            client.system.deleteSystem(session_key, module.params["id"], cleanup)
    except rpcFault as fault:
        client.auth.logout(session_key)
        module.fail_json(msg=f"Failed to delete system: {fault}")

    client.auth.logout(session_key)
    module.exit_json(changed=True)


if __name__ == "__main__":
    main()
