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
    pass

