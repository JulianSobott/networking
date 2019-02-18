"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import time

from networking.Logging import logger
from networking.Communication_general import SingleConnector, MultiConnector, MetaFunctionCommunicator


class ServerCommunicator(SingleConnector):
    pass


class MultiServerCommunicator(MultiConnector):
    pass


class ServerFunctions(metaclass=MetaFunctionCommunicator):
    communicator = None

