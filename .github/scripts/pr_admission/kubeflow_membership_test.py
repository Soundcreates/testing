#!/usr/bin/env python3
# Copyright The Kubeflow Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest import mock

from kubeflow_membership import _parse_members, is_kubeflow_member


class ParseMembersTest(unittest.TestCase):
    def test_combines_admins_and_members_case_insensitively(self):
        members = _parse_members(
            'orgs:\n'
            '  kubeflow:\n'
            '    admins: [Alice]\n'
            '    members: [BOB, alice]\n'
        )
        self.assertEqual(members, {'alice', 'bob'})

    def test_rejects_missing_empty_and_invalid_membership_data(self):
        invalid_documents = (
            '{}',
            'orgs:\n  kubeflow:\n    admins: []\n    members: []\n',
            'orgs:\n  kubeflow:\n    admins: [valid]\n    members: invalid\n',
            'orgs:\n  kubeflow:\n    admins: [bad_login!]\n    members: []\n',
        )
        for document in invalid_documents:
            with self.subTest(document=document), self.assertRaises(RuntimeError):
                _parse_members(document)

    def test_rejects_duplicate_mapping_keys(self):
        document = (
            'orgs:\n'
            '  kubeflow:\n'
            '    admins: [alice]\n'
            '    members: [bob]\n'
            '    members: [mallory]\n'
        )
        with self.assertRaises(RuntimeError):
            _parse_members(document)


class MembershipLookupTest(unittest.TestCase):
    @mock.patch('kubeflow_membership.subprocess.run')
    def test_uses_acl_and_matches_login_case_insensitively(self, run):
        run.return_value.stdout = (
            'orgs:\n'
            '  kubeflow:\n'
            '    admins: [Alice]\n'
            '    members: [bob]\n'
        )
        self.assertTrue(is_kubeflow_member('alice'))
        run.assert_called_once()

    @mock.patch('kubeflow_membership.subprocess.run')
    def test_rejects_invalid_login_before_api_call(self, run):
        with self.assertRaises(ValueError):
            is_kubeflow_member('invalid login')
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
