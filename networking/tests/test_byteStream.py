"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from unittest import TestCase

from networking.Data import ByteStream, pack_int


class TestByteStream(TestCase):

    def test_next_int(self):
        first_int = 102
        second_int = 2089
        example_byte_string = pack_int(first_int) + pack_int(second_int)
        byte_stream = ByteStream(example_byte_string)

        next_int = byte_stream.next_int()
        self.assertEqual(next_int, first_int)
        next_int = byte_stream.next_int()
        self.assertEqual(next_int, second_int)

    def test_next_bytes(self):
        example_byte_string = b"Hello World"
        byte_stream = ByteStream(example_byte_string)
        expected = b"Hello"
        actual = byte_stream.next_bytes(5)
        self.assertEqual(expected, actual)

    def test_next_bytes_error(self):
        example_byte_string = b"H"
        byte_stream = ByteStream(example_byte_string)
        self.assertRaises(IndexError, byte_stream.next_bytes, 5)
        self.assertRaises(AssertionError, byte_stream.next_bytes, -2)

