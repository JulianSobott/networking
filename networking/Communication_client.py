"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from typing import Optional

from networking.Logging import logger
from networking.Communication_general import SingleConnector, MultiConnector, Functions, Communicator


class ServerCommunicator(SingleConnector):
    """A static accessible class, that is responsible for communicating with the server.
    This class needs to be overwritten. The overwritten class needs to set the attributes :code:`local_functions` and
    :code:`remote_functions`. To call a function at the server type:
    :code:`ServerCommunicator.remote_functions.dummy_function(x, y)`
    """
    pass


class MultiServerCommunicator(MultiConnector):
    pass


class ServerFunctions(Functions):
    """Static class that contains all available server side functions. All functions must be stored in the
    :attr:`__dict__` attribute. To achieve this you have two options.

    1. One class :class:`ServerFunctions` used at client and server:
        * Directly import them with :code:`from server import dummy_function`
    2. Split client and server:
        * At the client redefine the server functions without implementation:
                :code:`def dummy_function(x, y): ...`
        * At the server either use the first option or redefine and call the implementation:
            :code:`def dummy_function(x, y): return server.dummy_function(x, y)`

        """
    pass

