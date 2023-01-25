import json
import unittest
from mock import patch, MagicMock
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


class ansible_exit_json(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class ansible_fail_json(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    raise ansible_exit_json(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise ansible_fail_json(kwargs)


class test_suma_module(unittest.TestCase):
    def set_module_args(self, args):
        if "_ansible_remote_tmp" not in args:
            args["_ansible_remote_tmp"] = "/tmp"
        if "_ansible_keep_remote_files" not in args:
            args["_ansible_keep_remote_files"] = False

        args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
        basic._ANSIBLE_ARGS = to_bytes(args)

    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

        self.login = MagicMock(return_value="1234")
        self.logout = MagicMock(return_value=1)
        self.mock_serverproxy_patch = patch("xmlrpc.client.ServerProxy")
        self.addCleanup(self.mock_serverproxy_patch.stop)
        self.mock_serverproxy = self.mock_serverproxy_patch.start()
        self.mock_serverproxy.return_value.auth.login = self.login
        self.mock_serverproxy.return_value.auth.logout = self.logout
