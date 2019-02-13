"""
@author: Julian Sobott
@created: 19.10.2018
@brief: Handling data for transmitting over network
@description:

Data Types that can be packed (and their limitations):
    int: 4 bytes
    float: None known
    str: max length ~2**32 (at larger strings the PC runs out of RAM and crashes)
    dict: None known
    tuple: None known
    bytes: None known
    bool: None
    NoneType: None

@external_use:

@internal_use:

"""
import json
import types as builtinTypes

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
    bool:   0x008,
    type(None):   0x009,
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
            value_bytes = bytes(value, ENCODING)
            byte_string += int.to_bytes(len(value_bytes), NUM_INT_BYTES, BYTEORDER)
            byte_string += value_bytes
        elif val_type is list:
            list_byte_string = _pack(*value)
            byte_string += int.to_bytes(len(list_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += list_byte_string
        elif val_type is dict:
            dict_byte_string = json.dumps(value).encode(ENCODING)
            byte_string += int.to_bytes(len(dict_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += dict_byte_string
        elif val_type is tuple:
            tuple_byte_string = _pack(*value)
            byte_string += int.to_bytes(len(tuple_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += tuple_byte_string
        elif val_type is bytes:
            byte_string += int.to_bytes(len(value), NUM_INT_BYTES, BYTEORDER)
            byte_string += value
        elif val_type is bool:
            byte_string += int.to_bytes(1, 1, BYTEORDER, signed=False) if value else int.to_bytes(0, 1, BYTEORDER, signed=False)
        elif isinstance(val_type(), type(None)):
            pass
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
            idx_end += NUM_INT_BYTES
            len_dict_string = int.from_bytes(byte_string[idx_start:idx_end], BYTEORDER)
            idx_start = idx_end
            idx_end += len_dict_string
            value = json.loads(byte_string[idx_start:idx_end].decode(ENCODING))
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
        elif isinstance(val_type(), type(None)):
            value = None
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


def pack_int_type(int_type):
    return int.to_bytes(int_type, NUM_TYPE_BYTES, BYTEORDER)


def unpack_int_type(full_byte_string):
    return int.from_bytes(full_byte_string[:NUM_TYPE_BYTES], BYTEORDER)


def example(name, second_name="Miller", tup=()):
    print("Hello: " + str(name) + " " + str(second_name) + " --> " + str(tup))
