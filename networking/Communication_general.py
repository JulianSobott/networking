"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
@Features: Better raise of excpetion : add file and linenumber, when packet return
"""
import threading
import socket
import time
from typing import Tuple, List, Dict, Optional, Callable, Any, Type, Union

import utils
from networking.Logging import logger
from networking.Packets import Packet, DataPacket, FunctionPacket, FileMetaPacket, Header, packets as packet_types
from networking.ID_management import IDManager, remove_manager
from networking.Data import ByteStream, File

SocketAddress = Tuple[str, int]

CLIENT_ID_END = 30
SERVER_ID_END = 0   # Max 30 servers


def to_client_id(id_):
    return int(id_ + CLIENT_ID_END)


def to_server_id(id_):
    return int(id_ + SERVER_ID_END)


class Communicator(threading.Thread):
    CHUNK_SIZE = 4096

    def __init__(self, address: SocketAddress, id_, socket_connection=socket.socket(), from_accept=False,
                 on_close: Optional[Callable[['Communicator'], Any]] = None, local_functions=Type['Functions']) -> None:
        super().__init__(name=f"{'Client' if from_accept else 'Server'}_Communicator_thread_{id_}")
        self._socket_connection = socket_connection
        self._address = address
        self._id = id_
        self._is_on = True
        self._is_connected = from_accept
        self._keep_connection = not from_accept
        self._packets: List[Packet] = []
        self._exit = threading.Event()
        self._time_till_next_check = 0.3
        self._on_close = on_close
        self._functions: Type['Functions'] = local_functions
        self._auto_execute_functions = from_accept
        self._closed = False
        self.wait_for_response_timeout = float("inf")

    def run(self) -> None:
        if not self._is_connected:
            self._connect()
        self._wait_for_new_input()

    def _connect(self, seconds_till_next_try=2, timeout=-1) -> bool:
        waited = 0
        while self._is_on and not self._is_connected:
            try:
                self._socket_connection = socket.create_connection(self._address)
                self._is_connected = True
                logger.info(f"Successfully connected to: {str(self._address)}")
                return True
            except ConnectionRefusedError:
                logger.warning("Could not connect to server with address: (%s)", str(self._address))
            except OSError as e:
                logger.error("Is already connected to server")
                logger.debug(e)
                self._is_connected = True
            except socket.gaierror:
                raise ValueError(
                    f"Address error. {self._address} is not a valid address. Address must be of type {SocketAddress}")

            self._exit.wait(seconds_till_next_try)
            waited += seconds_till_next_try
            if waited > timeout >= 0:
                logger.warning("Connection timeout")
                return False
        return False

    def _recv_data(self, size: int) -> Optional[bytes]:
        try:
            chunk_data = self._socket_connection.recv(size)
            if chunk_data == b"":
                logger.info("Connection reset, (%s)", str(self._address))
                self._is_connected = False
            else:
                return chunk_data

        except ConnectionResetError:
            if self._is_on:
                logger.warning(f"Connection reset at ID({self._id}), {self._address}")
            self._is_connected = False

        except ConnectionAbortedError:
            if self._is_on:
                logger.warning(f"Connection aborted at ID({self._id}), {self._address}")
            self._is_connected = False

        except OSError:
            if self._is_on:
                logger.warning("TCP connection closed while listening")
            self._is_connected = False

    def _wait_for_new_input(self):
        byte_stream = ByteStream(b'')
        while self._is_on:
            if self._is_on and not self._is_connected:
                if self._keep_connection:
                    self._connect()
                else:
                    self.stop(is_same_thread=True)
            packet = self._recv_packet(byte_stream)
            if packet is not None:
                if isinstance(packet, FileMetaPacket):
                    self._recv_file(packet, byte_stream)
                    self._packets.append(packet)
                elif self._auto_execute_functions and isinstance(packet, FunctionPacket):
                    func_thread = FunctionExecutionThread(self._id, packet, self._handle_packet)
                    func_thread.start()
                else:
                    self._packets.append(packet)

    def _recv_packet(self, byte_stream: ByteStream) -> Optional[Packet]:
        packet_builder = PacketBuilder(byte_stream)
        while True:
            chunk_data = self._recv_data(self.CHUNK_SIZE)
            if chunk_data == b"" or chunk_data is None:
                logger.info("Connection reset, (%s)", str(self._address))
                self._is_connected = False
                return None
            else:
                possible_packet = packet_builder.add_chunk(chunk_data)
                logger.debug(possible_packet)
                if possible_packet is not None:
                    return possible_packet

    @utils.time_func
    def _recv_file(self, file_meta_packet: FileMetaPacket, byte_stream: ByteStream) -> None:
        file_path = file_meta_packet.dst_path
        existing_bytes = byte_stream.next_all_bytes()
        with open(file_path, "wb+") as file:
            file.write(existing_bytes)
        remaining_bytes = file_meta_packet.file_size - len(existing_bytes)
        with open(file_path, "ab") as file:
            while remaining_bytes > 0:
                num_next_bytes = min(self.CHUNK_SIZE, remaining_bytes)
                data = self._recv_data(num_next_bytes)
                file.write(data)
                remaining_bytes -= len(data)

    def send_packet(self, packet: Packet) -> bool:
        IDManager(self._id).set_ids_of_packet(packet)
        send_data = packet.pack()
        successfully_sent = self._send_bytes(send_data)
        if not successfully_sent:
            logger.error("Could not send packet: %s", str(packet))
        return successfully_sent

    def _send_bytes(self, byte_string: bytes) -> bool:
        if not self._is_connected:
            self._connect(timeout=2)
        try:
            total_sent = 0
            data_size = len(byte_string)
            while total_sent < data_size:
                sent = self._socket_connection.send(byte_string[total_sent:])
                if sent == 0:
                    logger.warning(f"Could not send bytes {byte_string}")
                    self._is_connected = False
                    return False
                total_sent += sent
            self._is_connected = True
            return total_sent == data_size
        except OSError:
            logger.error(f"Could not send bytes {byte_string}")
            return False

    def wait_for_response(self):
        # TODO: add type hinting when implementation is finished
        waited = 0.
        while self._is_on:
            next_global_id = IDManager(self._id).get_next_outer_id()
            try:
                next_packet = self._packets.pop(0)
                actual_outer_id = next_packet.header.id_container.global_id
                if actual_outer_id > next_global_id:
                    logger.error(f"Packet lost! Expected outer_id: {next_global_id}. Got instead: {actual_outer_id}")
                    # TODO: handle
                elif actual_outer_id < next_global_id:
                    logger.error(f"Unhandled Packet! Expected outer_id: {next_global_id}. "
                                 f"Got instead: {actual_outer_id}")
                    # TODO: handle (if possible)
                else:
                    if isinstance(next_packet, FunctionPacket):
                        # execute and keep waiting for data
                        self._handle_packet(next_packet)
                    elif isinstance(next_packet, DataPacket):
                        self._handle_packet(next_packet)
                        return next_packet
                    elif isinstance(next_packet, FileMetaPacket):
                        return DataPacket(**{"return": File.from_meta_packet(next_packet)})
                    # if isinstance FileMetaPacket: wait till all data is saved to file (receive_file)
                    else:
                        logger.error(f"Received not implemented Packet class: {type(next_packet)}")

            except IndexError:
                pass  # List is empty -> wait
            self._exit.wait(self._time_till_next_check)
            waited += self._time_till_next_check
            if waited > self.wait_for_response_timeout >= 0:
                logger.warning("wait_for_response waited too long")
                raise TimeoutError("wait_for_response waited too long")

    def _handle_packet(self, packet):
        IDManager(self._id).update_ids_by_packet(packet)
        if isinstance(packet, FunctionPacket):
            self._received_function_packet(packet)

    def _received_function_packet(self, packet: FunctionPacket) -> None:
        func = packet.function_name
        args = packet.args
        kwargs = packet.kwargs
        try:
            ret_value = self._functions.__getattr__(func)(*args, **kwargs)
            if isinstance(ret_value, File):
                return self._send_file(ret_value)
        except TypeError as e:
            ret_value = e
        except AttributeError as e:
            ret_value = e

        ret_kwargs = {"return": ret_value}
        data_packet = DataPacket(**ret_kwargs)
        self.send_packet(data_packet)

    @utils.time_func
    def _send_file(self, file: File):
        file_meta_packet = FileMetaPacket(file.src_path, file.size, file.dst_path)
        self.send_packet(file_meta_packet)
        with open(file.src_path, "rb") as f:
            file_data = f.read(self.CHUNK_SIZE * 2)
            while len(file_data) > 0:
                self._socket_connection.send(file_data)
                file_data = f.read(self.CHUNK_SIZE * 2)

    def stop(self, is_same_thread=False) -> None:
        if self._closed:
            logger.debug("Prevented closing already closed communicator")
        else:
            logger.info(f"Stopping communicator: {self._id}")
            self._is_on = False
            self._exit.set()
            self._socket_connection.close()
            self._is_connected = False
            if not is_same_thread:
                self.join()
            remove_manager(self._id)
            if self._on_close is not None:
                try:
                    self._on_close(self)
                except TypeError:
                    pass  # no function provided
            self._closed = True

    def is_connected(self) -> bool:
        return self._is_connected

    def get_id(self) -> int:
        return self._id


class ByteDecoder:

    def __init__(self):
        self._packet_builder = PacketBuilder()
        self._file_receiver = FileReceiver()
        self.byte_stream = ByteStream(b"")
        self.current_header: Optional[Header] = None
        self.receiving_file = False

    def add_chunk(self, byte_string: bytes) -> Optional[Packet]:
        if self.receiving_file:
            file_data_size = self._file_receiver.file_size - self._file_receiver.received_bytes
            self._file_receiver.add_file_data(byte_string[:file_data_size])
            byte_string = byte_string[file_data_size:]
            if len(byte_string) > 0:
                self.receiving_file = False
        self.byte_stream += byte_string
        if not self.receiving_file:
            if self.current_header is None and self.byte_stream.length >= Header.LENGTH_BYTES:
                self.current_header = Header.from_bytes(self.byte_stream)
            if self.current_header and self.byte_stream.remaining_length >= self.current_header.specific_data_size:
                packet = Packet.from_bytes(self.current_header, self.byte_stream)
                if isinstance(packet, FileMetaPacket):
                    self.receiving_file = True
                self.byte_stream.remove_consumed_bytes()
                self.current_header = None
                return packet
        return None


class PacketBuilder:

    def __init__(self, byte_stream: ByteStream) -> None:
        self.byte_stream = byte_stream
        self.current_header: Optional[Header] = None

    def add_chunk(self, byte_string: bytes) -> Optional[Packet]:
        self.byte_stream += byte_string
        if self.current_header is None and self.byte_stream.length >= Header.LENGTH_BYTES:
            self.current_header = Header.from_bytes(self.byte_stream)
        if self.current_header and self.byte_stream.remaining_length >= self.current_header.specific_data_size:
            packet = Packet.from_bytes(self.current_header, self.byte_stream)
            self.byte_stream.remove_consumed_bytes()
            self.current_header = None
            return packet
        return None


class FileReceiver:

    def __init__(self) -> None:
        self.receiving_file = False
        self.received_bytes = 0
        self.file_size = 0
        self.dst_path = ""

    def set_file_meta_data(self, meta_packet: FileMetaPacket):
        self.file_size = meta_packet.file_size
        self.dst_path = meta_packet.dst_path

    def add_file_data(self, file_data: bytes) -> None:
        with open(self.dst_path, "wb+") as f:
            f.write(file_data)


class MetaFunctionCommunicator(type):

    def __call__(cls, *args, **kwargs):
        try:
            timeout = kwargs["timeout"]
            connector: Connector = cls.__getattr__("_connector")
            if connector and connector.communicator:
                connector.communicator.wait_for_response_timeout = timeout
        except KeyError:
            pass
        return cls

    def __getattribute__(self, item: str):
        if item == "__getattr__":
            return type.__getattribute__(self, item)
        if item == "__setattr__":
            return type.__setattr__
        if item == "__call__":
            return type.__call__
        if item.startswith("__", 0, 2):
            return type.__getattribute__(self, item)

        def container(*args, **kwargs) -> Any:
            function_name = item
            # send function packet
            connector: Connector = self.__getattr__("_connector")
            function_packet = FunctionPacket(function_name, *args, **kwargs)
            if connector is None or connector.communicator is None:
                raise ConnectionError(
                    "Communicator is not connected!"
                    "Connect first to a server with `ServerCommunicator.connect(server_address)´")
            sent_packet = connector.communicator.send_packet(function_packet)
            if not sent_packet:
                raise ConnectionError("Could not send function to server. Check connection to server.")

            try:
                data_packet = connector.communicator.wait_for_response()
            except TimeoutError as e:
                raise e
            # unpack data packet
            return_values = data_packet.data["return"]
            if isinstance(return_values, Exception):
                logger.exception(return_values)
                # An exception was thrown at the other side!
                raise return_values
            return return_values

        return container

    def __getattr__(self, item):
        func = type.__getattribute__(self, item)
        return func


class MetaSingletonConnector(type):
    _instances: Dict[int, 'Connector'] = {}

    def __call__(cls, *args, **kwargs) -> 'Connector':
        id_: int = args[0]
        if id_ not in cls._instances:
            cls._instances[id_] = super(MetaSingletonConnector, cls).__call__(*args, **kwargs)
        return cls._instances[id_]

    @classmethod
    def remove(mcs, id_: int) -> 'Connector':
        return mcs._instances.pop(id_)

    @classmethod
    def remove_all(mcs) -> Dict[int, 'Connector']:
        ret = dict(mcs._instances)
        mcs._instances = {}
        return ret


class Connector:
    remote_functions: Optional[Type['Functions']] = None
    local_functions: Optional[Type['Functions']] = None

    communicator: Optional[Communicator] = None
    _id = to_client_id(0)

    @staticmethod
    def connect(connector: Union['Connector', Type['SingleConnector']], addr: SocketAddress, blocking=True,
                timeout=float("inf")) -> bool:
        if connector.communicator is None:
            connector.communicator = Communicator(addr, id_=connector._id, local_functions=connector.local_functions)
            connector.remote_functions.__setattr__(connector.remote_functions, "_connector", connector)
            connector.communicator.start()

            def try_connect():
                waited = 0.
                wait_time = 0.01
                while not connector.communicator.is_connected() and waited < timeout:
                    time.sleep(wait_time)
                    waited += wait_time
                if waited >= timeout:
                    logger.warning(f"Stopped trying to connect to server after {int(waited)} seconds due to timeout")
                    connector.communicator.stop()
                    # raise TimeoutError(f"Stopped trying to connect to server after {int(waited)} seconds")
            if blocking:
                try_connect()
            else:
                threading.Thread(target=try_connect, name=f"Connector_{connector._id}").start()
        assert isinstance(connector.communicator, Communicator)
        return connector.communicator.is_connected()

    @staticmethod
    def close_connection(connector: Union['Connector', Type['SingleConnector']], blocking=True,
                         timeout=float("inf")) -> None:
        if connector.communicator is not None:
            connector.communicator.stop()
            if blocking:
                waited = 0.
                wait_time = 0.01
                while connector.communicator.is_connected() and waited < timeout:
                    time.sleep(wait_time)
                    waited += wait_time
            connector.communicator: Optional[Communicator] = None

    @staticmethod
    def is_connected(connector: Union['Connector', Type['SingleConnector']]) -> bool:
        if connector.communicator is None:
            return False
        return connector.communicator.is_connected()

    @property
    def id(self):
        return self._id


class MultiConnector(Connector, metaclass=MetaSingletonConnector):

    def __init__(self, id_: int) -> None:
        self._id = id_
        self.communicator: Optional[Communicator] = None

    def connect(self: Connector, addr: SocketAddress, blocking=True, timeout=float("inf")) -> bool:
        return super().connect(self, addr, blocking, timeout)

    def close_connection(self: Connector, blocking=True, timeout=float("inf")) -> None:
        return super().close_connection(self, blocking, timeout)

    @staticmethod
    def close_all_connections() -> None:
        all_instances = MetaSingletonConnector.remove_all()
        for id_, connector in all_instances.items():
            connector.close_connection(connector)

    def is_connected(self) -> bool:
        return super().is_connected(self)


class SingleConnector(Connector):
    """Only static accessible. Therefore only a single connector (per address) per machine possible"""

    @classmethod
    def connect(cls, addr: SocketAddress, blocking=True, timeout=float("inf")) -> bool:
        return super().connect(cls, addr, blocking, timeout)

    @classmethod
    def close_connection(cls, blocking=True, timeout=float("inf")) -> None:
        return super().close_connection(cls, blocking, timeout)

    @classmethod
    def is_connected(cls) -> bool:
        return super().is_connected(cls)


class Functions(metaclass=MetaFunctionCommunicator):
    """Static class that contains all available local and remote functions. All functions must be stored in the
        :attr:`__dict__` attribute.

            """
    _connector: Optional[Communicator] = None

    def __new__(cls, *args, **kwargs):
        pass


class FunctionExecutionThread(threading.Thread):

    def __init__(self, id_: int, function_packet: FunctionPacket, handle_packet: Callable) -> None:
        super().__init__(name=f"FunctionExecutionThread_{id_}")
        self._id = id_
        self._function_packet = function_packet
        self._handle_packet = handle_packet

    def run(self):
        self._handle_packet(self._function_packet)

    @property
    def id(self):
        return self._id
