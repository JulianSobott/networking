"""
:module: pynetworking.Data
:synopsis: Lowest level module, that manages important data for packets, mostly in bytes.
:author: Julian Sobott

public functions
----------------

.. autofunction:: general_pack

.. autofunction:: general_unpack

.. autofunction:: pack_int_type

.. autofunction:: unpack_int_type

.. autofunction:: pack_int

public classes
--------------

.. autoclass:: ByteStream
    :members:
    :undoc-members:

.. autoclass:: File
    :members:
    :undoc-members:

"""
import os
import dill

from pynetworking.utils import Ddict
from pynetworking.Logging import logger

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


def general_pack(*args) -> bytes:
    """Converts all args into a bytes string. """
    return dill.dumps(args)


def general_unpack(byte_stream: 'ByteStream', num_bytes=None) -> tuple:
    """Take in a bytestream, with the bytes string from :func:`general_pack`, and converts it back into a tuple with
    all args."""
    num_bytes = byte_stream.remaining_length if num_bytes is None else num_bytes
    bytes_string = byte_stream.next_bytes(num_bytes)
    data = dill.loads(bytes_string)
    return data


class ByteStream:
    """This class utilises the bytes object. Among other things, it stores the bytes string and the idx. All `next`
    functions move the idx."""

    def __init__(self, byte_string: bytes) -> None:
        self.byte_string = byte_string
        self.idx = 0
        self.length = len(byte_string)
        self.remaining_length = self.length
        self.reached_end = self.remaining_length <= 0

    def next_int(self) -> int:
        """Converts the next bytes into an integer."""
        byte_string = self.next_bytes(NUM_INT_BYTES)
        return int.from_bytes(byte_string, BYTEORDER, signed=True)

    def next_bytes(self, num_bytes: int) -> bytes:
        assert num_bytes >= 0, f"This function is not meant to be called with negative values ({num_bytes})"
        try:
            return self.byte_string[self.idx: self.idx + num_bytes]
        finally:
            self._inc_idx(num_bytes)
            if self.reached_end and self.idx > self.length:
                raise IndexError(f"Byte string ran out of scope: {self.idx} > {self.length}")

    def next_all_bytes(self) -> bytes:
        return self.next_bytes(self.remaining_length)

    def _inc_idx(self, amount: int) -> None:
        self.idx += amount
        self.remaining_length -= amount
        if self.remaining_length <= 0:
            self.reached_end = True

    def remove_consumed_bytes(self) -> None:
        """Deletes all bytes, that are before the idx. Resets all values to fit the new bytes string"""
        self.byte_string = self.byte_string[self.idx:]
        self.length = len(self.byte_string)
        self.remaining_length = self.length
        self.reached_end = self.length == 0
        self.idx = 0

    def __iadd__(self, other: bytes) -> 'ByteStream':
        if not isinstance(other, bytes):
            raise TypeError(f"{type(other)} is not type: bytes")
        self.byte_string += other
        added_length = len(other)
        self.length += added_length
        self.remaining_length += added_length
        self.reached_end = self.remaining_length <= 0
        return self

    def __repr__(self):
        return str(self.byte_string[:self.idx]) + "|" + str(self.byte_string[self.idx:])


class File:
    """This class represents a file that should be sent. If a file is to be sent, an object of this class shall be
    sent with the proper paths. This internally sends the file."""

    def __init__(self, src_path: str, dst_path: str, size=None) -> None:
        self.src_path = src_path
        self.dst_path = dst_path
        if size is None:
            self.size = os.path.getsize(src_path)
        else:
            self.size = size

    @classmethod
    def from_meta_packet(cls, file_meta_packet):
        return cls(file_meta_packet.src_path, file_meta_packet.dst_path, file_meta_packet.file_size)


def pack_int_type(int_type: int) -> bytes:
    """Packs a type described as an integer into bytes"""
    return int.to_bytes(int_type, NUM_TYPE_BYTES, BYTEORDER)


def unpack_int_type(full_byte_string: bytes) -> int:
    """Unpacks bytes into a type described as an integer"""
    return int.from_bytes(full_byte_string[:NUM_TYPE_BYTES], BYTEORDER)


def pack_int(num: int) -> bytes:
    """Packs any integer number into bytes"""
    return int.to_bytes(num, NUM_INT_BYTES, BYTEORDER, signed=True)
