"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net
from networking.Logging import logger
import Interface


def server_func():
    logger.debug(Interface.ClientCommunicator.communicator)
    ret_value = Interface.ClientCommunicator.remote_functions.client_func()
    print(f"Server: {ret_value}")
    return "Goodbye"


