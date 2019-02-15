"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import time
import threading
import socket

from networking.Logging import logger
from networking.Packets import Packet, DataPacket, FunctionPacket, Header
from networking.ID_management import IDManager, remove_manager
from networking.Data import ByteStream


class MetaFunctionCommunicator(type):

    _initialized = False

    @classmethod
    def init(mcs, communicator):
        mcs._communicator = communicator
        mcs._initialized = True

    def __getattribute__(self, item):
        if not self._initialized:
            return type.__getattribute__(self, item)

        def container(*args):
            function_name = item
            function_args = args
            # send function packet
            # recv data packet
            # unpack data packet
            data = None
            return data
        return container

    def send_function(cls, function_name, args, kwargs):
        pass

    def recv_function(cls, function_name, args, kwargs):
        ret_value = None
        try:
            func = type.__getattribute__(cls, function_name)
            try:
                ret_value = func(*args, **kwargs)
            except TypeError as e:
                ret_value = e
        except AttributeError as e:
            ret_value = e
        data_packet = DataPacket(ret_value=ret_value)
        cls._communicator: Communicator
        cls._communicator.send_packet(data_packet)

    def __getattr__(self, item):
        func = type.__getattribute__(self, item)
        return func


class InternServerCommunicator:

    def __init__(self, addr):
        self.communicator = Communicator(addr)
        self.communicator.start()


class ServerCommunicator(metaclass=MetaFunctionCommunicator):

    @classmethod
    def connect(cls, addr):
        communicator = Communicator(addr)
        communicator.start()
        cls.init(communicator)

    @staticmethod
    def close_connection():
        pass


class DummyServerCommunicator(ServerCommunicator):
    from networking.Packets import FunctionPacket

class ServerFunctions(metaclass=MetaFunctionCommunicator):
    from networking.Packets import FunctionPacket


#DummyServerCommunicator.FunctionPacket()

class Communicator(threading.Thread):

    CHUNK_SIZE = 1024

    def __init__(self, address, id_=0, socket_connection=None):
        super().__init__(name=f"Communicator_thread_{id}")
        self._socket_connection = socket_connection
        self._address = address
        self._id = id_
        self._is_on = True
        self._is_connected = socket_connection is not None
        self._packets = []

    def run(self):
        if not self._is_connected:
            self._connect()
        self._wait_for_new_input()

    def _connect(self, seconds_till_next_try=1, timeout=-1):
        waited = 0
        while self._is_on and not self._is_connected:
            try:
                self._socket_connection = socket.create_connection(self._address)
                self._is_connected = True
                logger.debug(f"Successfully connected to: {str(self._address)}")
            except ConnectionRefusedError:
                logger.warning("Could not connect to server with address: (%s)", str(self._address))
            except OSError as e:
                logger.error("Is already connected to server")
                logger.debug(e)
                self._is_connected = True

            time.sleep(seconds_till_next_try)
            waited += seconds_till_next_try
            if waited > timeout > 0:
                logger.warning("Connection timeout")
                return

    def _wait_for_new_input(self):
        packet_builder = PacketBuilder()
        while self._is_on:
            if not self._is_connected:
                self._connect()
            try:
                chunk_data = self._socket_connection.recv(self.CHUNK_SIZE)
                if chunk_data == b"":
                    logger.warning("Connection reset, (%s)", str(self._address))
                    self._is_connected = False
                else:
                    possible_packet = packet_builder.add_chunk(chunk_data)
                    if possible_packet is not None:
                        self._packets.append(possible_packet)

            except ConnectionResetError:
                logger.error("Connection reset, (%s)", str(self._address))
                self._is_connected = False

            except ConnectionAbortedError:
                logger.error("Connection aborted, (%s)", str(self._address))
                self._is_connected = False

            except OSError:
                logger.error("TCP connection closed while listening")
                self._is_connected = False

    def send_packet(self, packet):
        try:
            IDManager(self._id).set_ids_of_packet(packet)
            send_data = packet.pack()
            total_sent = 0
            data_size = len(send_data)
            while total_sent < data_size:
                sent = self._socket_connection.send(send_data[total_sent:])
                if sent == 0:
                    logger.error("Connection closed. Could not send packet")
                    self._is_connected = False
                total_sent += sent
            self._is_connected = True
        except OSError:
            logger.error("Could not send packet: %s", str(packet))

    def stop(self):
        self._is_on = False
        self._is_connected = False
        self._socket_connection.close()
        self.join()
        remove_manager(self._id)


class PacketBuilder:

    def __init__(self):
        self.byte_stream = ByteStream(b"")
        self.current_header = None

    def add_chunk(self, byte_string):
        self.byte_stream += byte_string
        if self.current_header is None and self.byte_stream.length >= Header.LENGTH_BYTES:
            self.current_header = Header.from_bytes(self.byte_stream)
        if self.current_header and self.byte_stream.remaining_length >= self.current_header.specific_data_size:
            packet = Packet.from_bytes(self.current_header, self.byte_stream)
            self.byte_stream.remove_consumed_bytes()
            return packet
        return None
