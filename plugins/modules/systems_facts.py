#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.apatard.suma.plugins.module_utils.suma_utils import (
    suma_connect,
)
from xmlrpc.client import Fault as rpcFault

DOCUMENTATION = """
---
module: systems_facts
author: "Arnaud Patard"
short_description: List SUMA systems ids
description:
   - Returns all registered systems ids.
options:
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
            hostname=dict(required=True),
            login=dict(required=True),
            password=dict(required=True, no_log=True),
            ssl_check=dict(required=False, type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    (client, session_key) = suma_connect(module)

    try:
        sys_list = client.system.listSystems(session_key)
    except rpcFault as fault:
        client.auth.logout(session_key)
        module.fail_json(msg=f"Failed to get system list: {fault}")

    sys_idlist = list(map(lambda d: d["id"], sys_list))
    try:
        net_syslist = client.system.getNetworkForSystems(session_key, sys_idlist)
    except rpcFault as fault:
        client.auth.logout(session_key)
        module.fail_json(msg=f"Failed to get network infos for system list: {fault}")

    client.auth.logout(session_key)
    facts = {}
    facts = {"suma_systems": net_syslist}
    module.exit_json(changed=False, ansible_facts=facts)


if __name__ == "__main__":
    main()
