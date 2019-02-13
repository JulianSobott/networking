"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from unittest import TestCase

from networking.Data import _pack, _unpack


def test_single_value(test_self, value):
    byte_string = _pack(value)
    new_value = _unpack(byte_string)[0]
    test_self.assertEqual(value, new_value)


class TestPacking(TestCase):

    def test_int(self):
        test_single_value(self, -890)

    def test_float(self):
        test_single_value(self, 212400.7598823849019)

    def test_str_special_chars(self):
        string = "!$Hqä \n}\t."
        test_single_value(self, string)

    def test_str_long(self):
        """Warning: strings with length more than 2**30 will crash the PC"""
        string = "W" * 2**20
        test_single_value(self, string)

    def test_list(self):
        value = [[i for i in range(2)]].append([i for i in range(2)])
        test_single_value(self, value)

    def test_dict(self):
        value = {"val1": 1, "väl2": "Hä llo", "val3": [2, 6]}
        test_single_value(self, value)

    def test_tuple(self):
        test_single_value(self, ("Hello", 10, [2, 0]))

    def test_bool(self):
        test_single_value(self, True)

    def test_bytes(self):
        test_single_value(self, b"Hello")

    def test_None(self):
        test_single_value(self, None)

