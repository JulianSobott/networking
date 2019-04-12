import pynetworking as net

server = None


class ServerFunctions(net.ServerFunctions):
    """All server functions, that can be called by the client"""
    from server import request_login


class ClientFunctions(net.ClientFunctions):
    """All client functions, that can be called by the server"""
    from client import get_username, get_password


class ServerCommunicator(net.ServerCommunicator):
    remote_functions = ServerFunctions
    local_functions = ClientFunctions


class ClientCommunicator(net.ClientCommunicator):
    remote_functions = ClientFunctions
    local_functions = ServerFunctions


server = ServerCommunicator.remote_functions
