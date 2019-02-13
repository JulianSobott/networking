"""
@author: Julian Sobott
@created: 19.10.2018
@brief: Handling data for transmitting over network
@description:
all available packets:
-Function_packet:
-Status_packet:
-Data_packet:
-File_meta_packet:

general packet byte string:
<packet_byte_string_len><function_id><inner_id><outer_id><packet_cls_id><specific_packet_data>


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

from .utils import Ddict
from .Logging import logger

NUM_TYPE_BYTES = 3
ENCODING = "utf-8"
BYTEORDER = "big"
NUM_INT_BYTES = 4


types = Ddict({
    int:    0x001,
    float:  0x002,
    str:    0x003,
    list:   0x004,
    dict:   0x005,
    tuple:  0x006,
    bytes:  0x007,
    bool:   0x008
})


def _pack(*args):
    byte_string = b""

    for value in args:
        val_type = type(value)
        try:
            type_num = types[val_type]
        except KeyError:
            raise KeyError()
        byte_string += type_num.to_bytes(NUM_TYPE_BYTES, BYTEORDER)

        if val_type is int:
            byte_string += int.to_bytes(value, NUM_INT_BYTES, BYTEORDER, signed=True)
        elif val_type is float:
            b_value = bytes(value.hex(), ENCODING)
            byte_string += int.to_bytes(len(b_value), NUM_INT_BYTES, BYTEORDER)
            byte_string += b_value
        elif val_type is str:
            byte_string += int.to_bytes(len(value), NUM_INT_BYTES, BYTEORDER)
            byte_string += bytes(value, ENCODING)
        elif val_type is list:
            list_byte_string = _pack(*value)
            byte_string += int.to_bytes(len(list_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += list_byte_string
        elif val_type is dict:
            byte_string += bytes(str(value), ENCODING)   # TODO: Find more performing and secure option
        elif val_type is tuple:
            tuple_byte_string = _pack(*value)
            byte_string += int.to_bytes(len(tuple_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += tuple_byte_string
        elif val_type is bytes:
            byte_string += int.to_bytes(len(value), NUM_INT_BYTES, BYTEORDER)
            byte_string += value
        elif val_type is bool:
            byte_string += int.to_bytes(1, 1, BYTEORDER, signed=False) if value else int.to_bytes(0, 1, BYTEORDER, signed=False)
        else:
            raise Exception("Unknown data type: " + str(val_type) + "\t(in Datatypes.Main.pack_values()")
    return byte_string


def _unpack(byte_string):
    values = []
    idx_start = 0
    idx_end = 0
    while len(byte_string[idx_start:]) > 0:
        idx_end += NUM_TYPE_BYTES
        b_type = byte_string[idx_start:idx_end]
        type_num = int.from_bytes(b_type, BYTEORDER)
        try:
            val_type = types[type_num]
        except KeyError:
            raise KeyError()
        idx_start = idx_end
        if val_type is int:
            idx_end += NUM_INT_BYTES
            value = int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER, signed=True)
        elif val_type is float:
            idx_end += NUM_INT_BYTES
            val_len = int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER)
            idx_start = idx_end
            idx_end += val_len
            value = float.fromhex(str(byte_string[idx_start:idx_end], ENCODING))
        elif val_type is str:
            idx_end += NUM_INT_BYTES
            val_len = int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER)
            idx_start = idx_end
            idx_end += val_len
            value = str(byte_string[idx_start:idx_end], ENCODING)
        elif val_type is list:
            idx_end += NUM_INT_BYTES
            len_list_string = int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER)
            idx_start = idx_end
            idx_end += len_list_string
            value = list(_unpack(byte_string[idx_start:idx_end]))
        elif val_type is dict:
            byte_string += bytes(str(value), ENCODING)   # TODO: Find more performing and secure option
        elif val_type is tuple:
            idx_end += NUM_INT_BYTES
            len_tuple_string = int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER)
            idx_start = idx_end
            idx_end += len_tuple_string
            value = tuple(_unpack(byte_string[idx_start:idx_end]))
        elif val_type is bytes:
            idx_end += NUM_INT_BYTES
            val_len = int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER)
            idx_start = idx_end
            idx_end += val_len
            value = byte_string[idx_start:idx_end]
        elif val_type is bool:
            idx_start = idx_end
            idx_end += 1
            value = True if int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER, signed=False) == 1 else False
        else:
            raise Exception("Unknown data type: " + str(val_type) + "\t(in " + str(__name__) + ".pack_values()")

        idx_start = idx_end
        values.append(value)
    return tuple(values)


class IDContainer:

    TOTAL_BYTE_LENGTH = 3 * NUM_INT_BYTES + 3 * NUM_TYPE_BYTES

    def __init__(self, function_id, inner_id, outer_id):
        self.function_id = function_id
        self.inner_id = inner_id
        self.outer_id = outer_id

    def pack(self):
        byte_string = _pack(self.function_id, self.inner_id, self.outer_id)
        return byte_string

    @staticmethod
    def unpack(byte_string):
        function_id, inner_id, outer_id = _unpack(byte_string[:IDContainer.TOTAL_BYTE_LENGTH])
        return IDContainer(function_id, inner_id, outer_id)

    def set_ids(self, function_id, inner_id, outer_id):
        self.function_id = function_id
        self.inner_id = inner_id
        self.outer_id = outer_id

    def get_ids(self):
        return self.function_id, self.inner_id, self.outer_id

    def __str__(self):
        return str(self.function_id) + " - " + str(self.inner_id) + " - " + str(self.outer_id)

    def __eq__(self, other):
        if not isinstance(other, IDContainer):
            return False
        return (self.function_id == other.function_id and
                self.inner_id == other.inner_id and
                self.outer_id == other.outer_id)


class Packet:

    def __init__(self, packet):
        self.packet_ID = packets[packet.__class__]
        self.id_container = IDContainer(-1, -1, -1)

    def pack(self):
        byte_string = b""
        byte_string += self.id_container.pack()
        byte_string += pack_int_type(self.packet_ID)
        return byte_string

    @staticmethod
    def unpack(byte_string):
        len_packet_string = int.from_bytes(byte_string[:NUM_INT_BYTES], BYTEORDER, signed=False)
        byte_string = byte_string[NUM_INT_BYTES: NUM_INT_BYTES + len_packet_string]
        extra_bytes = byte_string[NUM_INT_BYTES + len_packet_string:]

        id_container = IDContainer.unpack(byte_string)

        packet_id = unpack_int_type(byte_string[IDContainer.TOTAL_BYTE_LENGTH:])
        all_data = byte_string[IDContainer.TOTAL_BYTE_LENGTH + NUM_TYPE_BYTES:]
        if packet_id not in packets.values():
            raise ValueError("Error: Unknown packet ID: (" + str(packet_id) + ")")
        packet = packets[packet_id].unpack(all_data)
        packet.set_ids(*id_container.get_ids())
        return packet, extra_bytes

    def set_ids(self, function_id, inner_id, outer_id):
        self.id_container.set_ids(function_id, inner_id, outer_id)

    def __eq__(self, other):
        if isinstance(other, Packet):
            return self.id_container == other.id_container and self.packet_ID == other.packet_ID
        else:
            return False

    def __str__(self):
        return packets[self.packet_ID].__name__ + ": " + str(self.id_container) + "\n\t"


class Function_packet(Packet):

    def __init__(self, func, *args):
        super().__init__(self)
        if type(func) is str:
            self.function_name = func
        else:
            self.function_name = func.__name__
        self.data = args

    def execute(self, connection, functions):
        func = functions.get_function(self.function_name)
        func(connection, *self.data)

    @staticmethod
    def unpack(byte_string):
        all_data = _unpack(byte_string)
        function_name = all_data[0]
        args = all_data[1]
        packet = Function_packet(function_name, *args)
        return packet

    def pack(self):
        byte_string = b""
        byte_string += super().pack()
        byte_string += _pack(self.function_name, self.data)

        len_string = len(byte_string)
        b_len_string = int.to_bytes(len_string, NUM_INT_BYTES, BYTEORDER, signed=False)

        return b_len_string + byte_string

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, Function_packet):
            return self.function_name == other.function_name and self.data == other.data
        else:
            return False

    def __str__(self):
        string = super().__str__()
        string += str(self.function_name)
        string += str(self.data)
        return string


class Status_packet(Packet):

    class Status_code(Enum):
        successful = 0
        failed = 1

    def __init__(self, status_code, text="", last_in_func=True):
        super().__init__(self)
        self.status_code = status_code
        self.text = text
        self.last_in_func = last_in_func

    def pack(self):
        byte_string = b""
        byte_string += super().pack()
        val_status_code = self.status_code.value
        byte_string += _pack(val_status_code, self.text, self.last_in_func)
        len_string = len(byte_string)
        b_len_string = int.to_bytes(len_string, NUM_INT_BYTES, BYTEORDER, signed=False)
        return b_len_string + byte_string

    @staticmethod
    def unpack(byte_string):
        all_data = _unpack(byte_string)
        status_code = all_data[0]
        text = all_data[1]
        last_in_func = all_data[2]

        return Status_packet(Status_packet.Status_code(status_code), text, last_in_func)

    def is_success(self):
        return self.status_code == Status_packet.Status_code.successful

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, Status_packet):
            return self.status_code == other.status_code and self.text == other.text
        else:
            return self.status_code == Status_packet.Status_code.successful

    def __str__(self):
        string = super().__str__()
        string += str(self.status_code)
        string += ": \""
        string += str(self.text)
        string += "\""
        return string


class Data_packet(Packet):

    def __init__(self, data_name, *args):
        super().__init__(self)
        self.name = data_name
        self.data = args

    @staticmethod
    def unpack(byte_string):
        all_data = _unpack(byte_string)
        data_name = all_data[0]
        args = all_data[1]
        packet = Data_packet(data_name, *args)
        return packet

    def pack(self):
        byte_string = b""
        byte_string += super().pack()

        byte_string += _pack(self.name, self.data)
        len_string = len(byte_string)
        b_len_string = int.to_bytes(len_string, NUM_INT_BYTES, BYTEORDER, signed=False)
        return b_len_string + byte_string

    @staticmethod
    def get_empty_size(data_name):
        length = IDContainer.TOTAL_BYTE_LENGTH
        length += NUM_TYPE_BYTES
        length += len(_pack(data_name))
        length += NUM_INT_BYTES
        length += 14    # Length of tuple
        return length

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, Data_packet):
            return self.name == other.name and self.data == other.data
        else:
            return False

    def __str__(self):
        string = super().__str__()
        string += str(self.name)
        string += str(self.data)
        return string


class File_meta_packet(Data_packet):

    def __init__(self, abs_path):
        if os.path.exists(abs_path):
            self.file_name = os.path.split(abs_path)[1]
            self.extension = os.path.splitext(abs_path)[1]
            self.size = os.path.getsize(abs_path)
        else:
            self.file_name = "NULL"
            self.extension = "NULL"
            self.size = 0
        super().__init__("file meta data", self.file_name, self.extension, self.size)

    def set_attributes(self, name, extension, size):
        self.file_name = name
        self.extension = extension
        self.size = size
        super().__init__("file meta data", self.file_name, self.extension, self.size)

    def pack(self):
        byte_string = b""
        byte_string += super().pack()
        return byte_string

    @staticmethod
    def unpack(byte_string):
        all_data = _unpack(byte_string)
        packet = File_meta_packet("None")
        name = all_data[1][0]
        extension = all_data[1][1]
        size = all_data[1][2]
        packet.set_attributes(name, extension, size)
        return packet

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, File_meta_packet):
            return self.file_name == other.file_name and self.extension == other.extension and self.size == other.size
        else:
            return False

    def __str__(self):
        string = super().__str__()
        # string += "File_meta_data: "
        # string += str(self.name) + " (" + str(self.size) + ")"
        return string


packets = Ddict({
    Function_packet:    0x101,
    Status_packet:      0x102,
    Data_packet:        0x103,
    File_meta_packet:   0x104
})


def pack_int_type(int_type):
    return int.to_bytes(int_type, NUM_TYPE_BYTES, BYTEORDER)


def unpack_int_type(full_byte_string):
    return int.from_bytes(full_byte_string[:NUM_TYPE_BYTES], BYTEORDER)


def example(name, second_name="Miller", tup=()):
    print("Hello: " + str(name) + " " + str(second_name) + " --> " + str(tup))


if __name__ == "__main__":
    """ DEBUGGING """
    p = Status_packet(Status_packet.Status_code.successful)
    logger.debug(str(p))