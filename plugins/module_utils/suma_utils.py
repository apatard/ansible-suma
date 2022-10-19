from xmlrpc.client import ServerProxy
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
        client = ServerProxy(manager_url, context=context, use_datetime=True)
    except socket.gaierror:
        module.fail_json(msg="Failed to connect")

    try:
        session_key = client.auth.login(
            module.params["login"], module.params["password"]
        )
    except rpcFault as fault:
        module.fail_json(msg=f"Failed to login: {fault}")

    return (client, session_key)
