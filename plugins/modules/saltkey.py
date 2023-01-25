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
module: suma_saltkey
author: "Arnaud Patard"
short_description: Handle suse manager salt keys
description:
   - Accepts/Deletes/Rejects suse manager salt keys
options:
   key:
     description:
        - name of the key
     required: true
   state:
     description:
        - state of the key (accepted / rejected / absent)
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
            key=dict(required=True),
            state=dict(
                required=True,
                choices=["accepted", "absent", "rejected"],
            ),
            hostname=dict(required=True),
            login=dict(required=True),
            password=dict(required=True, no_log=True),
            ssl_check=dict(required=False, type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    saltkey = module.params["key"]

    (client, session_key) = suma_connect(module)

    try:
        accepted_keylist = client.saltkey.acceptedList(session_key)
        pending_keylist = client.saltkey.pendingList(session_key)
        rejected_keylist = client.saltkey.rejectedList(session_key)
    except rpcFault as fault:
        module.fail_json(msg=f"Failed to get key infos: {fault}")

    keylist = accepted_keylist + pending_keylist + rejected_keylist
    if saltkey not in keylist:
        if module.params["state"] == "absent":
            client.auth.logout(session_key)
            module.exit_json(changed=False)
        client.auth.logout(session_key)
        module.fail_json(msg="Key not found")

    if module.params["state"] == "accepted":
        if saltkey in accepted_keylist:
            client.auth.logout(session_key)
            module.exit_json(changed=False)
        if saltkey not in pending_keylist:
            client.auth.logout(session_key)
            module.fail_json(msg="Key neither accepted nor pending")
        if not module.check_mode:
            try:
                client.saltkey.accept(session_key, saltkey)
            except rpcFault as fault:
                client.auth.logout(session_key)
                module.fail_json(msg=f"Failed to accept : {fault}")
        client.auth.logout(session_key)
        module.exit_json(changed=True)
    elif module.params["state"] == "absent":
        if not module.check_mode:
            try:
                client.saltkey.delete(session_key, saltkey)
            except rpcFault as fault:
                client.auth.logout(session_key)
                module.fail_json(msg=f"Failed to delete : {fault}")
        client.auth.logout(session_key)
        module.exit_json(changed=True)
    elif module.params["state"] == "rejected":
        if saltkey in rejected_keylist:
            client.auth.logout(session_key)
            module.exit_json(changed=False)
        if saltkey not in pending_keylist:
            client.auth.logout(session_key)
            module.fail_json(msg="Key neither rejected nor pending")
        if not module.check_mode:
            try:
                client.saltkey.reject(session_key, saltkey)
            except rpcFault as fault:
                client.auth.logout(session_key)
                module.fail_json(msg=f"Failed to reject : {fault}")
        client.auth.logout(session_key)
        module.exit_json(changed=True)

    client.auth.logout(session_key)
    module.fail_json(msg="Should not be reached")


if __name__ == "__main__":
    main()
