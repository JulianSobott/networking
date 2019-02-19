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
from Packets import FunctionPacket, DataPacket


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

    def test_one_func_packet(self):
        packet = FunctionPacket("dummy")
        IDManager(0).set_ids_of_packet(packet)
        expected_ids = (0, 0)
        self.assertEqual(expected_ids, packet.header.id_container.get_ids())
        expected_function_stack = [0]
        self.assertEqual(expected_function_stack, IDManager(0).get_function_stack())

    def test_ids_func_data(self):
        func_packet = FunctionPacket("dummy")    # Client
        IDManager(0).set_ids_of_packet(func_packet)
        expected = (0, 0, 0)
        self.assertEqual(expected, func_packet.header.id_container.get_ids())
        expected = ()

        data_packet = DataPacket(ret="Nothing")
        IDManager(0).set_ids_of_packet(data_packet)
        expected = (0, 0, 0)
        self.assertEqual(expected, func_packet.header.id_container.get_ids())
