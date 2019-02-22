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


def greet_client(name: str):
    print(f"Hello {name}")
    ret_value = net.ClientPool.get().remote_functions.client_func("Paukl")
    if ret_value:
        print("Cool you responded")
    else:
        print("Mhhh something went wrong ")
    return "Goodbye"


def server_faculty(number: int) -> int:
    if number <= 1:
        return number
    return number * net.ClientPool.get().remote_functions.client_faculty(number - 1)


