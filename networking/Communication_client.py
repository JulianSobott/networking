"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from typing import Optional

from Logging import logger
from Communication_general import SingleConnector, MultiConnector, MetaFunctionCommunicator, Communicator


class ServerCommunicator(SingleConnector):
    pass


class MultiServerCommunicator(MultiConnector):
    pass


class ServerFunctions(metaclass=MetaFunctionCommunicator):
    communicator: Optional[Communicator] = None

