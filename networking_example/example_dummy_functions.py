"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""

called = False


def dummy_no_arg_no_ret():
    global called
    called = True
    print("Dummy function called")
