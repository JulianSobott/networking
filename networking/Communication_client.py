"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from typing import Union, Type

from Logging import logger
from Communication_general import Connector, SingleConnector, MultiConnector, Functions, Communicator, SocketAddress
from Packets import DataPacket
from Data import Cryptographer


class ServerCommunicator(SingleConnector):

    @classmethod
    def connect(cls, addr: SocketAddress, blocking=True, timeout=float("inf")):
        connected = super().connect(addr, blocking, timeout)
        if connected:
            exchange_keys(cls)


class MultiServerCommunicator(MultiConnector):
    def connect(self, addr: SocketAddress, blocking=True, timeout=float("inf")):
        connected = super().connect(addr, blocking, timeout)
        if connected:
            exchange_keys(self)


class ServerFunctions(Functions):
    pass


def exchange_keys(connector: Union['Connector', Type['SingleConnector']]):
    # generate public key + private key TODO
    public_key = b"public_key"
    private_key = b"private_key"
    # send public key
    public_key_packet = DataPacket(public_key=public_key)
    connector.communicator.send_packet(public_key_packet)
    # wait for communication key
    communication_packet = connector.communicator.wait_for_response()
    encrypted_communication_key = communication_packet.data["communication_key"]
    # decrypt key with private key TODO
    communication_key = encrypted_communication_key
    # set communication key
    Cryptographer.set_key(communication_key)
