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
short_description: Set system entitlements / add-on
description:
   - Set system entitlements / add-on
options:
   id:
     description:
        - system id
     required: true
     type: int
   addon:
     description:
        - List of entitlements to enable/disable
     type: list
     elements: str
     required: true
   state:
     description:
        - Enable/Disable add-on(s)
     required: true
     type: str
     choices: [ absent, present ]
   hostname:
     description:
        - host running the Suse Manager instance.
     required: true
     type: str
   login:
     description:
        - account on the Suse Manager instance.
     required: true
     type: str
   password:
     description:
        - password of the suse manager account
     required: true
     type: str
   ssl_check:
     description:
        - disable SSL check *dangerous*
     required: false
     type: bool
"""

AVAILABLE_ADDONS = {
    "container_build_host",
    "monitoring_entitled",
    "osimage_build_host",
    "virtualization_host",
    "ansible_control_node",
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            id=dict(required=True, type="int"),
            addon=dict(required=True, type="list", elements="str"),
            state=dict(required=True, choices=["present", "absent"]),
            hostname=dict(required=True),
            login=dict(required=True),
            password=dict(required=True, no_log=True),
            ssl_check=dict(required=False, type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    addons = set(module.params["addon"])

    inval_addon = set(addons) - set(AVAILABLE_ADDONS)
    if len(inval_addon) != 0:
        module.fail_json(msg=f"Invalid add-ons: {','.join(inval_addon)}")

    (client, session_key) = suma_connect(module)

    try:
        cur_en_addons = set(
            client.system.getEntitlements(session_key, module.params["id"])
        )
    except rpcFault as fault:
        client.auth.logout(session_key)
        module.fail_json(msg=f"Failed to get system add-ons list: {fault}")
    cur_dis_addons = AVAILABLE_ADDONS - cur_en_addons

    # systems have salt_entitled when managed by salt
    # So, "hide" it
    if "salt_entitled" in cur_en_addons:
        cur_en_addons.remove("salt_entitled")

    if module.params["state"] == "absent":
        if cur_dis_addons == addons:
            client.auth.logout(session_key)
            module.exit_json(changed=False)
        diff = {
            "before": f"{','.join(cur_en_addons)}\n",
            "after": f"{','.join(cur_en_addons - addons)}\n",
        }
        if module.check_mode:
            client.auth.logout(session_key)
            module.exit_json(changed=True, diff=diff)
        try:
            client.system.removeEntitlements(
                session_key, module.params["id"], list(addons)
            )
        except rpcFault as fault:
            client.auth.logout(session_key)
            module.fail_json(msg=f"Failed to get remove add-on: {fault}")

        client.auth.logout(session_key)
        module.exit_json(changed=True, diff=diff)

    if module.params["state"] == "present":
        if cur_en_addons == addons:
            client.auth.logout(session_key)
            module.exit_json(changed=False)
        diff = {
            "before": f"{','.join(cur_en_addons)}\n",
            "after": f"{','.join(addons)}\n",
        }
        if module.check_mode:
            client.auth.logout(session_key)
            module.exit_json(changed=True, diff=diff)
        try:
            client.system.addEntitlements(
                session_key, module.params["id"], list(addons)
            )
        except rpcFault as fault:
            client.auth.logout(session_key)
            module.fail_json(msg=f"Failed to get add add-on: {fault}")

        client.auth.logout(session_key)
        module.exit_json(changed=True, diff=diff)

    client.auth.logout(session_key)
    module.fail_json(msg="Should not be reached")


if __name__ == "__main__":
    main()
