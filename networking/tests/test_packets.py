"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

"""
import unittest

from networking.Packets import Header, Data_packet
from networking.Data import ByteStream


class TestPackets(unittest.TestCase):

    def test_function_packet(self):
        fp_first = Data.Function_packet(Data.example, "John", "Miller", (12, 13))
        b = fp_first.pack()
        fp_second, _ = Data.Packet.unpack(b)
        self.assertEqual(fp_first, fp_second)

    def test_status_packet(self):
        fp_first = Data.Status_packet(Data.Status_packet.Status_code.successful, "WRONG_AUTHENTICATION_DATA", False)
        b = fp_first.pack()
        fp_second, _ = Data.Packet.unpack(b)
        self.assertEqual(fp_first, fp_second)

    def test_data_packet(self):
        fp_first = Data.Data_packet("Name", "John Miller")
        b = fp_first.pack()
        fp_second, _ = Data.Packet.unpack(b)
        self.assertEqual(fp_first, fp_second)

    def test_file_meta_packet(self):
        fp_first = Data.File_meta_packet("Testing_Data.py")
        b = fp_first.pack()
        fp_second, _ = Data.Packet.unpack(b)
        self.assertEqual(fp_first, fp_second)


class TestHeader(unittest.TestCase):

    def test_packing(self):
        packet = Data_packet("Test", 10)
        header1_0 = packet.header
        byte_string = packet.pack()
        byte_stream = ByteStream(byte_string)
        header1_1 = Header.from_bytes(byte_stream)
        self.assertEqual(header1_0, header1_1)
