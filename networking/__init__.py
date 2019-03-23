"""
High level network communication

This tool abstracts network communication to a level, where the end user don`t has to care about
network communication. Server side functions can be called at the client as they were local and vise versa.
Functions may be called with parameters and may return values.

"""
from networking.Communication_client import ServerCommunicator, ServerFunctions, MultiServerCommunicator
from networking.Communication_server import ClientCommunicator, ClientFunctions, ClientManager
from networking.Data import File
import networking.utils
import networking.Logging

networking.Logging.logger.setLevel(20)
