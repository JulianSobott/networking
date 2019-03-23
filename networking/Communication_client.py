"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from typing import Union, Type, Optional

from networking.Logging import logger
from networking.Communication_general import SingleConnector, MultiConnector, Functions, Communicator
import networking.Communication_general
from networking.Communication_general import Connector, SingleConnector, MultiConnector, Functions, Communicator, SocketAddress
from networking.Packets import DataPacket
from networking.ID_management import IDManager


class ServerCommunicator(SingleConnector):
    """A static accessible class, that is responsible for communicating with the server.
        This class needs to be overwritten. The overwritten class needs to set the attributes :code:`local_functions` and
        :code:`remote_functions`. To call a function at the server type:
        :code:`ServerCommunicator.remote_functions.dummy_function(x, y)`
        """

    @classmethod
    def connect(cls, addr: SocketAddress, blocking=True, timeout=float("inf"), **kwargs) -> bool:
        connected = super().connect(addr, blocking, timeout, exchange_keys)
        return connected


class MultiServerCommunicator(MultiConnector):
    """A class that allows in contrast to the :class:`ServerCommunicator` multiple instances. This class also needs
    to be overwritten, just like :class:`ServerCommunicator`. To create and use call :code:`MultiServerCommunicator(n)`,
    where n is any number below 30. The object may not be stored, but can be called in different parts of the Code and
    the same object is returned, like a Singleton.
    """

    def connect(self, addr: SocketAddress, blocking=True, timeout=float("inf"), **kwargs) -> bool:
        connected = super().connect(addr, blocking, timeout, exchange_keys)
        return connected


class ServerFunctions(Functions):
    """Static class that contains all available server side functions. All functions must be stored in the
    :attr:`__dict__` attribute."""
    pass


def exchange_keys(connector: Union['Connector', Type['SingleConnector']]):
    # generate public key + private key
    cryptographer = connector.communicator.cryptographer
    cryptographer.generate_pgp_key_pair()
    serialized_public_key = cryptographer.get_serialized_public_key()
    IDManager(connector.get_id()).append_dummy_functions(2)
    # send public key
    public_key_packet = DataPacket(public_key=serialized_public_key)
    connector.communicator.send_packet(public_key_packet)
    # wait for communication key
    communication_packet = connector.communicator.wait_for_response()
    encrypted_communication_key = communication_packet.data["communication_key"]
    # decrypt key with private key
    communication_key = cryptographer.decrypt_pgp_msg(encrypted_communication_key)
    # set communication key
    cryptographer.communication_key = communication_key
    connector._exchanged_keys = True
