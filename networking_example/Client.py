"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net
from Interface import ServerCommunicator

if __name__ == '__main__':
    ServerCommunicator.connect(("127.0.0.1", "5000"))
    print(ServerCommunicator.dummy_func("John"))

