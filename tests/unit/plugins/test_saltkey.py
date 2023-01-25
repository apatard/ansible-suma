from ansible_collections.apatard.suma.plugins.modules import (
    saltkey,
)

from ansible_collections.apatard.suma.tests.unit.modules.utils import (
    ansible_exit_json,
    ansible_fail_json,
    test_suma_module,
)

import xmlrpc

from mock import Mock
import unittest


class test_suma_saltkey(test_suma_module):
    def __init__(self, *args, **kwargs):
        super(test_suma_saltkey, self).__init__(*args, **kwargs)
        self.base_args = {
            "hostname": "localhost.localdomain",
            "login": "login",
            "password": "password",
        }

    def setUp(self):
        super(test_suma_saltkey, self).setUp()
        ret_value = self.mock_serverproxy.return_value
        ret_value.saltkey.acceptedList.return_value = [
            "accepted1.example.com",
            "accepted2.example.com",
        ]
        ret_value.saltkey.pendingList.return_value = [
            "pending1.example.com",
            "pending2.example.com",
        ]
        ret_value.saltkey.rejectedList.return_value = [
            "rej1.example.com",
            "rej2.example.com",
        ]

    def set_args(self, args):
        args.update(self.base_args)
        self.set_module_args(args)

    @unittest.skip("To implement")
    def test_login_error(self):
        self.assertTrue(True)

    def test_key_not_found(self):
        self.set_args({"key": "notfound.example.com", "state": "accepted"})

        with self.assertRaises(ansible_fail_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["failed"])
        self.assertTrue(result.exception.args[0]["msg"] == "Key not found")
        self.assertEqual(self.logout.call_count, 1)

    # Tests for state: accepted
    def test_accept_key_rejected(self):
        self.set_args({"key": "rej2.example.com", "state": "accepted"})

        with self.assertRaises(ansible_fail_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["failed"])
        self.assertTrue(
            result.exception.args[0]["msg"] == "Key neither accepted nor pending"
        )
        self.assertEqual(self.logout.call_count, 1)

    def test_accept_key_already_accepted(self):
        self.set_args({"key": "accepted1.example.com", "state": "accepted"})

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertFalse(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)

    def test_accept_key_pending(self):
        self.set_args({"key": "pending1.example.com", "state": "accepted"})
        self.mock_serverproxy.return_value.saltkey.accept.return_value = 1

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)

    def test_accept_key_accept_fail(self):
        self.set_args({"key": "pending1.example.com", "state": "accepted"})
        self.mock_serverproxy.return_value.saltkey.accept = Mock(
            side_effect=xmlrpc.client.Fault(123, "")
        )

        with self.assertRaises(ansible_fail_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["failed"])
        self.assertTrue(
            result.exception.args[0]["msg"] == "Failed to accept : <Fault 123: ''>"
        )
        self.assertEqual(self.logout.call_count, 1)

    def test_accept_key_pending_check_mode(self):
        self.set_args(
            {
                "key": "pending1.example.com",
                "state": "accepted",
                "_ansible_check_mode": True,
            }
        )
        self.mock_serverproxy.return_value.saltkey.accept = Mock(
            side_effect=xmlrpc.client.Fault(123, "")
        )

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)
        self.assertEqual(
            self.mock_serverproxy.return_value.saltkey.accept.call_count, 0
        )

    # Tests for state: rejected
    def test_reject_key_rejected(self):
        self.set_args({"key": "accepted1.example.com", "state": "rejected"})

        with self.assertRaises(ansible_fail_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["failed"])
        self.assertTrue(
            result.exception.args[0]["msg"] == "Key neither rejected nor pending"
        )
        self.assertEqual(self.logout.call_count, 1)

    def test_reject_key_already_rejected(self):
        self.set_args({"key": "rej1.example.com", "state": "rejected"})

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertFalse(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)

    def test_reject_key_pending(self):
        self.set_args({"key": "pending1.example.com", "state": "rejected"})
        self.mock_serverproxy.return_value.saltkey.accept.return_value = 1

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)

    def test_reject_key_reject_fail(self):
        self.set_args({"key": "pending1.example.com", "state": "rejected"})
        self.mock_serverproxy.return_value.saltkey.reject = Mock(
            side_effect=xmlrpc.client.Fault(123, "")
        )

        with self.assertRaises(ansible_fail_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["failed"])
        self.assertTrue(
            result.exception.args[0]["msg"] == "Failed to reject : <Fault 123: ''>"
        )
        self.assertEqual(self.logout.call_count, 1)

    def test_reject_key_pending_check_mode(self):
        self.set_args(
            {
                "key": "pending1.example.com",
                "state": "rejected",
                "_ansible_check_mode": True,
            }
        )
        self.mock_serverproxy.return_value.saltkey.reject = Mock(
            side_effect=xmlrpc.client.Fault(123, "")
        )

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)
        self.assertEqual(
            self.mock_serverproxy.return_value.saltkey.reject.call_count, 0
        )

    # Tests for state: absent
    def test_delete_key_already_deleted(self):
        self.set_args({"key": "deleted.example.com", "state": "absent"})

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertFalse(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)

    def test_delete_key(self):
        self.set_args({"key": "pending1.example.com", "state": "absent"})
        self.mock_serverproxy.return_value.saltkey.accept.return_value = 1

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)

    def test_delete_key_fail(self):
        self.set_args({"key": "pending1.example.com", "state": "absent"})
        self.mock_serverproxy.return_value.saltkey.delete = Mock(
            side_effect=xmlrpc.client.Fault(123, "")
        )

        with self.assertRaises(ansible_fail_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["failed"])
        self.assertTrue(
            result.exception.args[0]["msg"] == "Failed to delete : <Fault 123: ''>"
        )
        self.assertEqual(self.logout.call_count, 1)

    def test_delete_key_check_mode(self):
        self.set_args(
            {
                "key": "pending1.example.com",
                "state": "absent",
                "_ansible_check_mode": True,
            }
        )
        self.mock_serverproxy.return_value.saltkey.delete = Mock(
            side_effect=xmlrpc.client.Fault(123, "")
        )

        with self.assertRaises(ansible_exit_json) as result:
            saltkey.main()
        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(self.logout.call_count, 1)
        self.assertEqual(
            self.mock_serverproxy.return_value.saltkey.delete.call_count, 0
        )
