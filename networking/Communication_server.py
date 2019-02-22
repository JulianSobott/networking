"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import threading
import socket
from typing import Dict, Type

from Logging import logger
from Communication_general import Communicator, Connector, MetaFunctionCommunicator, SocketAddress, Functions, \
    MultiConnector, to_server_id


class MetaClientManager(type):
    _instances: Dict[int, 'ClientManager'] = {}
    _last_instance: 'ClientManager'

    def __call__(cls, *args, **kwargs) -> 'ClientManager':
        address: int = args[0]
        if address not in cls._instances:
            MetaClientManager._instances[address] = super(MetaClientManager, cls).__call__(*args, **kwargs)
            MetaClientManager._last_instance = cls._instances[address]
        return MetaClientManager._instances[address]

    @staticmethod
    def get_proper_communicator(address=None):
        current_thread = threading.current_thread()
        try:
            id_ = current_thread._id
            try:
                if address is None:
                    manager = MetaClientManager._last_instance
                else:
                    try:
                        manager = MetaClientManager._instances[address]
                    except KeyError:
                        logger.error(f"No ClientManager started with address: {address}")
                        raise ConnectionError()
                return manager.clients[id_]
            except KeyError:
                logger.error(
                    f"Trying to access a client that was never connected! {manager.clients}: {id_}")
        except AttributeError:
            logger.error(
                "Captain we have a multithreading problem! Thread dependent function called from another thread")

    @staticmethod
    def tear_down():
        while len(MetaClientManager._instances.values()) > 0:
            client_manager: ClientManager = MetaClientManager._instances.popitem()[1]
            client_manager.stop_listening()
            client_manager.stop_connections()


class ClientManager(threading.Thread, metaclass=MetaClientManager):

    def __init__(self, address: SocketAddress, client_communicator: Type['ClientCommunicator']) -> None:
        super().__init__(name="ClientManager")
        self._socket_connection = socket.socket()
        self.clients: Dict[int, ClientCommunicator] = {}
        self._next_client_id = 0
        self._is_on = True
        self._address = address
        self._exit = threading.Event()
        self._client_communicator = client_communicator

    def run(self) -> None:
        try:
            self._socket_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket_connection.bind(self._address)
            logger.debug(f"Server is now listening on: {self._address[0]}:{self._address[1]}")
        except OSError:
            # [WinError 10038] socket closed before
            self._is_on = False

        self._socket_connection.listen(4)
        while self._is_on:
            try:
                (connection, addr) = self._socket_connection.accept()
                logger.info("New client connected: (%s)", str(addr))
                client_id = self._produce_next_client_id()
                client_communicator_id = to_server_id(client_id)
                client = self._client_communicator(client_communicator_id, self._address, connection,
                                                   self.remove_disconnected_client)
                self.clients[client_communicator_id] = client
            except OSError:
                if self._is_on:
                    logger.error("TCP connection closed while listening")
                    # TODO: handle (if possible)

    def _produce_next_client_id(self) -> int:
        try:
            return self._next_client_id
        finally:
            self._next_client_id += 1

    def remove_disconnected_client(self, communicator: Communicator) -> None:
        """Called when one side stops"""
        try:
            self.clients.pop(communicator.get_id())
        except KeyError:
            logger.error(f"Trying to remove a client that was never connected! {self.clients}: {communicator.get_id()}")

    def stop_listening(self) -> None:
        self._is_on = False
        self._socket_connection.close()
        self.join()
        logger.info("Closed server listener")

    def stop_connections(self) -> None:
        while len(self.clients.items()) > 0:
            client_id = self.clients.keys().__iter__().__next__()
            client = self.clients[client_id]
            client.close_connection()

    def __enter__(self) -> 'ClientManager':
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop_listening()
        self.stop_connections()


class ClientCommunicator(MultiConnector):

    def __init__(self, id_, address, connection, on_close):
        super().__init__(id_)
        self.communicator = Communicator(address, id_, connection, from_accept=True, on_close=on_close,
                                         local_functions=self.local_functions)
        self.communicator.start()
        self.remote_functions.__setattr__(self.remote_functions, "_connector", self)


class ClientFunctions(Functions):
    pass
