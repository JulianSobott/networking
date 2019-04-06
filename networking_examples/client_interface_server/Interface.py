"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import pynet as net


class ServerFunctions(net.ServerFunctions):
    from Server import greet_client, server_faculty


class ClientFunctions(net.ClientFunctions):
    from Client import client_faculty, client_func


class ServerCommunicator(net.ServerCommunicator):
    remote_functions = ServerFunctions
    local_functions = ClientFunctions


class ClientCommunicator(net.ClientCommunicator):
    remote_functions = ClientFunctions
    local_functions = ServerFunctions



