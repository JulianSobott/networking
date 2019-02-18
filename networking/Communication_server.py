"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import threading
import socket

from networking.Logging import logger
from networking.Communication_general import Communicator, Connector, MetaFunctionCommunicator


class NewConnectionListener(threading.Thread):

    def __init__(self, address):
        super().__init__(name="NewConnectionListener")
        self._socket_connection = socket.socket()
        self.clients = {}
        self._next_client_id = 0
        self._is_on = True
        self._address = address
        self._exit = threading.Event()

    def run(self):
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
                client = Communicator(self._address, client_id, connection, from_accept=True,
                                      on_close=self.remove_disconnected_client)
                client.start()
                self.clients[client_id] = client
            except OSError:
                if self._is_on:
                    logger.error("TCP connection closed while listening")
                    # TODO: handle (if possible)

    def _produce_next_client_id(self):
        try:
            return self._next_client_id
        finally:
            self._next_client_id += 1

    def remove_disconnected_client(self, communicator):
        """Called when one side stops"""
        try:
            self.clients.pop(communicator.get_id())
        except KeyError:
            logger.error(f"Trying to remove a client that was never connected! {self.clients}: {communicator.get_id()}")

    def stop_listening(self):
        self._is_on = False
        self._socket_connection.close()
        self.join()
        logger.info("Closed server listener")

    def stop_connections(self):
        while len(self.clients.items()) > 0:
            client_id = self.clients.keys().__iter__().__next__()
            client = self.clients[client_id]
            client.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_listening()
        self.stop_connections()


class ClientCommunicator(Connector):
    pass


class ClientFunctions(metaclass=MetaFunctionCommunicator):
    pass
