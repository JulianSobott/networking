"""
High level network communication

This tool abstracts network communication to a level, where the end user don`t has to care about
network communication. Server side functions can be called at the client as they were local and vise versa.
Functions may be called with parameters and may return values.

"""
from pynet.Communication_client import ServerCommunicator, ServerFunctions, MultiServerCommunicator
from pynet.Communication_server import ClientCommunicator, ClientFunctions, ClientManager
from pynet.Data import File
import pynet.utils
import pynet.Logging

pynet.Logging.logger.setLevel(20)
