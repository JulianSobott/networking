"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""


def dummy_no_arg_no_ret():
    print(f"Dummy function called")


def dummy_args_ret(name: str) -> tuple:
    from networking.tests.test_Communication import ClientCommunicator
    c = ClientCommunicator
    print(c.communicator)
    print(name)
    return 10, 10
