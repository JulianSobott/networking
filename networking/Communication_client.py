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
    pass


class MultiServerCommunicator(MultiConnector):
    pass


class ServerFunctions(Functions):
    pass

