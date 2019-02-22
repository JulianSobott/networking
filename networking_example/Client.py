"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net
from networking.Logging import logger
#from Interface import ServerCommunicator, ClientCommunicator
import Interface


def client_func(name) -> bool:
    print(f"Hello {name}")
    return True


if __name__ == '__main__':
    address = ("127.0.0.1", 5000)
    with net.ClientManager(address, Interface.ClientCommunicator):
        Interface.ServerCommunicator.connect(address)
        ret_value = Interface.ServerCommunicator.remote_functions.greet_client("John")
        print(f"Client: {ret_value}")
        Interface.ServerCommunicator.close_connection()

