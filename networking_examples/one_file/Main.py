"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net

server_address = "127.0.0.1", 5000


class ClientFunctions(net.ClientFunctions):
    @staticmethod
    def greet_server():
        return ServerCommunicator.remote_functions.say_hello("Walter")

    @staticmethod
    def say_hello(name: str) -> str:
        return f"Client: Hello {name}"


class ServerFunctions(net.ServerFunctions):
    @staticmethod
    def greet_client():
        return net.ClientPool.get().remote_functions.say_hello("Walter")

    @staticmethod
    def say_hello(name: str) -> str:
        return f"Server: Hello {name}"


class ClientCommunicator(net.ClientCommunicator):
    local_functions = ServerFunctions
    remote_functions = ClientFunctions


class ServerCommunicator(net.ServerCommunicator):
    local_functions = ClientFunctions
    remote_functions = ServerFunctions


def main():
    with net.ClientManager(server_address, ClientCommunicator):
        ServerCommunicator.connect(server_address)
        ret = ServerCommunicator.remote_functions.say_hello("Doris")
        print(ret)
        ret = ServerCommunicator.remote_functions.greet_client()
        print(ret)
        ServerCommunicator.close_connection()


if __name__ == '__main__':
    main()
