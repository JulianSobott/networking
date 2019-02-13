"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

"""
import unittest

import networking.Data as Data


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
