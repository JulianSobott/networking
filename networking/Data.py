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

@TODO_:

"""
from typing import Tuple, Any
from utils import Ddict, load_dict_from_json, dump_dict_to_json
from Logging import logger

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


def _pack(*args) -> bytes:
    byte_string = b""

    for value in args:
        val_type: type = type(value)
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
            try:
                dict_byte_string = dump_dict_to_json(value).encode(ENCODING)
            except TypeError as e:
                e.args = (f"Only objects of the following types are packable: ({types.keys()}", )
                raise
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


def _unpack(bytes_) -> tuple:
    if isinstance(bytes_, bytes):
        byte_stream = ByteStream(bytes_)
    else:
        byte_stream = bytes_
    values = []
    while not byte_stream.reached_end:
        type_num = int.from_bytes(byte_stream.next_bytes(NUM_TYPE_BYTES), BYTEORDER)
        try:
            val_type = types[type_num]
        except KeyError:
            raise KeyError()
        value: Any
        if val_type is int:
            value = byte_stream.next_int()
        elif val_type is float:
            val_len = byte_stream.next_int()
            value = float.fromhex(str(byte_stream.next_bytes(val_len), ENCODING))
        elif val_type is str:
            val_len = byte_stream.next_int()
            value = str(byte_stream.next_bytes(val_len), ENCODING)
        elif val_type is list:
            len_list_string = byte_stream.next_int()
            value = list(_unpack(byte_stream.next_bytes(len_list_string)))
        elif val_type is dict:
            len_dict_string = byte_stream.next_int()
            value = load_dict_from_json(byte_stream.next_bytes(len_dict_string).decode(ENCODING))
        elif val_type is tuple:
            len_tuple_string = byte_stream.next_int()
            value = tuple(_unpack(byte_stream.next_bytes(len_tuple_string)))
        elif val_type is bytes:
            val_len = byte_stream.next_int()
            value = byte_stream.next_bytes(val_len)
        elif val_type is bool:
            value = True if int.from_bytes(byte_stream.next_bytes(1), BYTEORDER, signed=False) == 1 else False
        elif isinstance(val_type(), type(None)):
            value = None
        else:
            raise Exception("Unknown data type: " + str(val_type) + "\t(in " + str(__name__) + ".pack_values()")
        values.append(value)
    return tuple(values)


class IDContainer:

    TOTAL_BYTE_LENGTH = 3 * NUM_INT_BYTES + 3 * NUM_TYPE_BYTES

    def __init__(self, function_id: int, inner_id: int, outer_id: int) -> None:
        self.function_id = function_id
        self.inner_id = inner_id
        self.outer_id = outer_id

    @classmethod
    def default_init(cls):
        return cls.__call__(-1, -1, -1)

    def pack(self) -> bytes:
        byte_string = pack_int(self.function_id)
        byte_string += pack_int(self.inner_id)
        byte_string += pack_int(self.outer_id)
        return byte_string

    @classmethod
    def from_bytes(cls, byte_stream: 'ByteStream') -> 'IDContainer':
        function_id = byte_stream.next_int()
        inner_id = byte_stream.next_int()
        outer_id = byte_stream.next_int()
        return cls.__call__(function_id, inner_id, outer_id)

    def set_ids(self, function_id: int, inner_id: int, outer_id: int):
        self.function_id = function_id
        self.inner_id = inner_id
        self.outer_id = outer_id

    def get_ids(self) -> Tuple[int, int, int]:
        return self.function_id, self.inner_id, self.outer_id

    def __repr__(self):
        return f"IDContainer({str(self.function_id)}, {str(self.inner_id)}, {str(self.outer_id)})"

    def __eq__(self, other):
        if not isinstance(other, IDContainer):
            return False
        return (self.function_id == other.function_id and
                self.inner_id == other.inner_id and
                self.outer_id == other.outer_id)


class ByteStream:

    def __init__(self, byte_string: bytes) -> None:
        self.byte_string = byte_string
        self.idx = 0
        self.length = len(byte_string)
        self.remaining_length = self.length
        self.reached_end = False

    def next_int(self) -> int:
        byte_string = self.next_bytes(NUM_INT_BYTES)
        return int.from_bytes(byte_string, BYTEORDER, signed=True)

    def next_bytes(self, num_bytes: int) -> bytes:
        assert num_bytes > 0, "This function is not meant to be called with negative values"
        try:
            return self.byte_string[self.idx: self.idx + num_bytes]
        finally:
            self._inc_idx(num_bytes)
            if self.reached_end and self.idx > self.length:
                raise IndexError("Byte string ran out of scope")

    def _inc_idx(self, amount: int) -> None:
        self.idx += amount
        self.remaining_length -= amount
        if self.remaining_length <= 0:
            self.reached_end = True

    def remove_consumed_bytes(self) -> None:
        self.byte_string = self.byte_string[self.idx:]
        self.length = len(self.byte_string)
        self.remaining_length = self.length
        self.reached_end = self.length == 0
        self.idx = 0

    def __iadd__(self, other: bytes) -> 'ByteStream':
        if not isinstance(other, bytes):
            raise TypeError
        self.byte_string += other
        added_length = len(other)
        self.length += added_length
        self.remaining_length += added_length
        self.reached_end = added_length > 0
        return self

    def __repr__(self):
        return str(self.byte_string)


def pack_int_type(int_type: int) -> bytes:
    return int.to_bytes(int_type, NUM_TYPE_BYTES, BYTEORDER)


def unpack_int_type(full_byte_string: bytes) -> int:
    return int.from_bytes(full_byte_string[:NUM_TYPE_BYTES], BYTEORDER)


def pack_int(num: int) -> bytes:
    return int.to_bytes(num, NUM_INT_BYTES, BYTEORDER, signed=True)

