"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

"""
import unittest

from networking.Packets import Header, Packet, DataPacket, FunctionPacket
from networking.Data import ByteStream
from networking.Logging import logger


class TestPackets(unittest.TestCase):

    def helper_packet_tests(self, packet):
        packet_one = packet
        byte_string = packet_one.pack()
        byte_stream = ByteStream(byte_string)
        header = Header.from_bytes(byte_stream)
        packet_two = Packet.from_bytes(header, byte_stream)
        self.assertEqual(packet_one, packet_two)

    def test_function_packet(self):
        packet = FunctionPacket(example_function, "John", "Miller", (12, 13))
        self.helper_packet_tests(packet)

        packet = FunctionPacket(example_function, "John", tup=("HE",))
        self.helper_packet_tests(packet)

    def test_status_packet(self):
        fp_first = Data.Status_packet(Data.Status_packet.Status_code.successful, "WRONG_AUTHENTICATION_DATA", False)
        b = fp_first.pack()
        fp_second, _ = Data.Packet.unpack(b)
        self.assertEqual(fp_first, fp_second)

    def test_data_packet(self):
        packet = DataPacket(Name="John Miller")
        self.helper_packet_tests(packet)

        packet = DataPacket(username="John", age="28", password=["he", "he"])
        self.helper_packet_tests(packet)

        packet = DataPacket.from_complex(classObj=TestHeader())
        self.helper_packet_tests(packet)

    def test_file_meta_packet(self):
        fp_first = Data.File_meta_packet("Testing_Data.py")
        b = fp_first.pack()
        fp_second, _ = Data.Packet.unpack(b)
        self.assertEqual(fp_first, fp_second)


class TestHeader(unittest.TestCase):

    def test_packing(self):
        packet = DataPacket(Test=10)
        header1_0 = packet.header
        byte_string = packet.pack()
        byte_stream = ByteStream(byte_string)
        header1_1 = Header.from_bytes(byte_stream)
        self.assertEqual(header1_0, header1_1)


def example_function(name, second_name="Miller", tup=()):
    print("Hello: " + str(name) + " " + str(second_name) + " --> " + str(tup))
