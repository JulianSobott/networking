"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

@TODO: test id's when packets are implemented
"""
from unittest import TestCase

from networking.ID_management import *


class TestIDManager(TestCase):

    def test_multiple_same_managers(self):
        manager1_0 = IDManager(1)
        manager1_1 = IDManager(1)
        self.assertEqual(manager1_0, manager1_1)

    def test_multiple_different_managers(self):
        manager1 = IDManager(1)
        manager2 = IDManager(2)
        self.assertNotEqual(manager1, manager2)

    def test_remove_manager(self):
        manager1_0 = IDManager(1)
        remove_manager(1)
        manager1_1 = IDManager(1)
        self.assertNotEqual(manager1_0, manager1_1)
