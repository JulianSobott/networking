"""
@author: Julian Sobott
@brief:
@description:

all available packets:
-FunctionPacket:
-DataPacket:


general packet byte string:
<packet_byte_string_len><function_id><global_id><packet_cls_id><specific_packet_data>


GeneralPacket:
    Header:
        - PacketType (Function, Data)
        - ID's
        - specific data size
    Specific Data:

@external_use:
packet = <cls>_packet(args)
byte_string = packet.pack()
same_packet = Packet.unpack(byte_string)


@internal_use:
New <cls>_packet:
    extend from packet
    implement: pack, unpack, __eq__, __str__
    add to packets
"""
from enum import Enum
import os
import pickle
from typing import Union, Dict, Any, Callable

from utils import Ddict
from Logging import logger
from Data import IDContainer, pack_int_type, unpack_int_type, NUM_INT_BYTES, BYTEORDER, NUM_TYPE_BYTES, general_unpack, \
    general_pack, ByteStream, pack_int, ENCODING


class Header:
    LENGTH_BYTES = 19

    def __init__(self, id_container: IDContainer, packet_type: int, specific_data_size: int) -> None:
        self.id_container = id_container
        self.packet_type = packet_type
        self.specific_data_size = specific_data_size

    @classmethod
    def from_packet(cls, packet: 'Packet') -> 'Header':
        packet_type = packets[packet.__class__]
        id_container = IDContainer.default_init()
        specific_data_size = 0
        return cls.__call__(id_container, packet_type, specific_data_size)

    @classmethod
    def from_bytes(cls, byte_stream: ByteStream) -> 'Header':
        id_container = IDContainer.from_bytes(byte_stream)
        packet_type = unpack_int_type(byte_stream.next_bytes(NUM_TYPE_BYTES))
        specific_data_size = byte_stream.next_int()
        return cls.__call__(id_container, packet_type, specific_data_size)

    def pack(self, len_packet_data: int) -> bytes:
        """id's + packet_type + len_packet_data"""
        self.specific_data_size = len_packet_data
        byte_string = b""
        byte_string += self.id_container.pack()
        byte_string += pack_int_type(self.packet_type)
        byte_string += pack_int(len_packet_data)
        return byte_string

    def __eq__(self, other):
        if not isinstance(other, Header):
            return False
        return (self.id_container == other.id_container and
                self.packet_type == other.packet_type and
                self.specific_data_size == other.specific_data_size)

    def __repr__(self):
        return (f"Header({self.id_container.__repr__()}, "
                f"{packets[self.packet_type].__name__}, {self.specific_data_size})\n\t")


class Packet:

    def __init__(self, packet: Union['FunctionPacket', 'DataPacket']) -> None:
        self.header = Header.from_packet(packet)

    def pack(self):
        pass

    def _pack_all(self, specific_data_bytes) -> bytes:
        byte_string = b""
        data_length = len(specific_data_bytes)
        byte_string += self.header.pack(data_length)
        byte_string += specific_data_bytes
        return byte_string

    @classmethod
    def from_bytes(cls, header: Header, byte_stream: ByteStream) -> Union['FunctionPacket', 'DataPacket']:
        if header.packet_type not in packets.values():
            raise ValueError("Unknown packet ID: (" + str(header.packet_type) + ")")
        packet = packets[header.packet_type].from_bytes(header, byte_stream)
        packet.header = header
        return packet

    def set_ids(self, function_id: int, outer_id: int) -> None:
        assert isinstance(function_id, int) and isinstance(outer_id, int), f"Ids must be int: ({function_id, outer_id}"
        self.header.id_container.set_ids(function_id, outer_id)

    def __eq__(self, other):
        if isinstance(other, Packet):
            return self.header == other.header
        else:
            return False

    def __repr__(self):
        return str(self.header)


class DataPacket(Packet):
    """Packet to send named data"""

    def __init__(self, **kwargs) -> None:
        super().__init__(self)
        self.data = kwargs

    @classmethod
    def from_bytes(cls, header: Header, byte_stream: ByteStream) -> 'DataPacket':
        num_bytes = header.specific_data_size
        data = general_unpack(byte_stream, num_bytes)[0]
        return cls.__call__(**data)

    def pack(self) -> bytes:
        specific_byte_string = general_pack(self.data)
        return super()._pack_all(specific_byte_string)

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, DataPacket):
            return self.data == other.data
        else:
            return False

    def __repr__(self):
        string = super().__repr__()
        string += str(self.data)
        return string


class FunctionPacket(Packet):

    def __init__(self, func: Union[Callable, str], *args, **kwargs) -> None:
        super().__init__(self)
        if type(func) is str:
            self.function_name: str = func
        else:
            self.function_name: str = func.__name__
        self.args: tuple = args
        self.kwargs: Dict[str, Any] = kwargs

    def execute(self, connection, functions):
        pass
        # TODO: implement

    @classmethod
    def from_bytes(cls, header: Header, byte_stream: ByteStream) -> 'FunctionPacket':
        num_bytes = header.specific_data_size
        all_data = general_unpack(byte_stream, num_bytes)
        function_name: str = all_data[0]
        args: tuple = all_data[1]
        kwargs: dict = all_data[2]
        return cls.__call__(function_name, *args, **kwargs)

    def pack(self) -> bytes:
        specific_byte_string = general_pack(self.function_name, self.args, self.kwargs)
        return super()._pack_all(specific_byte_string)

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, FunctionPacket):
            return self.function_name == other.function_name and self.args == other.args and self.kwargs == other.kwargs
        else:
            return False

    def __repr__(self):
        return f"{super().__repr__()} => FunctionPacket({str(self.function_name)}, " \
            f"{str(self.args)}, {str(self.kwargs)})"


packets = Ddict({
    FunctionPacket: 0x101,
    DataPacket: 0x103,
})
