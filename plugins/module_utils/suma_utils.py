# Copyright (c) 2022, Arnaud Patard <apatard@hupstream.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import xmlrpc.client
from xmlrpc.client import Fault as rpcFault
import socket
import ssl


def suma_connect(module):
    manager_url = "https://" + module.params["hostname"] + "/rpc/api"

    context = ssl.create_default_context()
    if module.params["ssl_check"] is False:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    try:
        client = xmlrpc.client.ServerProxy(
            manager_url, context=context, use_datetime=True
        )
    except socket.gaierror:
        module.fail_json(msg="Failed to connect")

    try:
        session_key = client.auth.login(
            module.params["login"], module.params["password"]
        )
    except rpcFault as fault:
        module.fail_json(msg=f"Failed to login: {fault}")
    except xmlrpc.client.ProtocolError as fault:
        module.fail_json(msg=f"Failed to login: {fault}")
    except socket.gaierror:
        module.fail_json(msg="Failed to connect")

    return (client, session_key)
