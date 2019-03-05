"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import threading
import socket
from typing import Dict, Type, Union, Optional

from networking.Logging import logger
from networking.Communication_general import Communicator, Connector, MetaFunctionCommunicator, SocketAddress, \
    Functions, \
    MultiConnector, to_server_id

__all__ = ["ClientPool", "ClientManager", "ClientFunctions"]


class ClientPool(type):
    """This class stores a instance of every client connected to the server. The instances can be accessed over the get
    function."""
    _instances: Dict[SocketAddress, Dict[int, 'ClientCommunicator']] = {}
    _last_address = None

    def __call__(cls, client_id, address, connection, on_close):
        if address not in ClientPool._instances:
            ClientPool._instances[address]: Dict[int, 'ClientCommunicator'] = {}
            ClientPool._last_address = address
        if client_id not in ClientPool._instances[address]:
            ClientPool._instances[address][client_id] = super(ClientPool, cls).__call__(client_id, address, connection,
                                                                                        on_close)
        return ClientPool._instances[address][client_id]

    @staticmethod
    def get(client_id: Optional[int] = None, server_address: Optional[SocketAddress] = None) -> 'ClientCommunicator':
        """Returns the proper ClientCommunicator. The proper one is the one who called the server-side function. This
        function is thread dependent. So if you create a new thread inside the called function you have to store the
        :code:`id` of the current ClientCommunicator and then call this function with this id as optional parameter.
        """
        if server_address is None:
            server_address = ClientPool._last_address
            if server_address is None:
                raise Exception("No client connected. Can only be called when a client connects to the server")
        if client_id is None:
            current_thread: Union[ClientCommunicator, threading.Thread] = threading.current_thread()
            try:
                client_id = current_thread.id
            except AttributeError:
                """Function may only be called from same thread (thread that called the server function) 
                or with a valid existing client_id!"""
                logger.error(
                    "Captain we have a multithreading problem! Thread dependent function called from another thread")
                raise Exception("Thread dependent function called from another thread")
        if client_id not in ClientPool._instances[server_address]:
            raise Exception("No client connected. Can only be called when a client connects to the server")
        assert isinstance(ClientPool._instances[server_address][client_id], ClientCommunicator), \
            "Previous checks didnt handle all cases"
        return ClientPool._instances[server_address][client_id]

    @staticmethod
    def tear_down():
        """Closes all server-side client connections"""
        while len(ClientPool._instances.values()) > 0:
            addresses = ClientPool._instances.popitem()[1]
            while len(addresses.values()) > 0:
                client_communicator: ClientCommunicator = addresses.popitem()[1]
                client_communicator.close_connection()
                client_communicator.close_connection()


class MetaClientManager(type):
    """Allows that multiple ClientManagers can be created. Stores every instance of a ClientManager"""
    _instances: Dict[SocketAddress, 'ClientManager'] = {}
    _last_instance: 'ClientManager'

    def __call__(cls, *args, **kwargs) -> 'ClientManager':
        address: SocketAddress = args[0]
        if address not in cls._instances:
            MetaClientManager._instances[address] = super(MetaClientManager, cls).__call__(*args, **kwargs)
            MetaClientManager._last_instance = cls._instances[address]
        return MetaClientManager._instances[address]

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
            logger.info(f"Server is now listening on: {self._address[0]}:{self._address[1]}")
            self._socket_connection.listen(4)
        except OSError as e:
            # [WinError 10038] socket closed before
            logger.error(e)
            self._is_on = False
        except socket.gaierror:
            raise ValueError(
                f"Address error. {self._address} is not a valid address. Address must be of type {SocketAddress}")

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


class ClientCommunicator(Connector, metaclass=ClientPool):
    """A static accessible class, that is responsible for communicating with a client.
    This class only needs to be overwritten, but is only used internally. The overwritten class needs to set the
    attributes :code:`local_functions` and :code:`remote_functions`. """

    def __init__(self, id_: int, address: SocketAddress, connection: socket.socket, on_close):
        super().__init__()
        self._id = id_
        self.communicator = Communicator(address, id_, connection, from_accept=True, on_close=on_close,
                                         local_functions=self.local_functions)
        self.communicator.start()
        self.remote_functions.__setattr__(self.remote_functions, "_connector", self)

    def close_connection(self: Connector, blocking=True, timeout=float("inf")) -> None:
        return super().close_connection(self, blocking, timeout)

    @property
    def id(self):
        return self._id


class ClientFunctions(Functions):
    """Static class that contains all available client side functions. All functions must be stored in the
    :attr:`__dict__` attribute."""
    pass
