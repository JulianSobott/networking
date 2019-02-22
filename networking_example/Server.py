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
    #logger.debug(net.MetaClientManager._instances)
    #logger.debug(net.MetaClientManager.get_proper_communicator())
    ret_value = net.MetaClientManager.get_proper_communicator().remote_functions.client_func("Paukl")
    print(f"Server: {ret_value}")
    return "Goodbye"


