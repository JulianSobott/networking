"""
@author: Julian Sobott
@brief: A example that shows very brief all important features of the networking module
@description:
This is example is meant to demonstrate the use of the most important features of the networking module.
This example has to be adjusted if you want to implement a real client server application. Here client and
server are executed in the same process which is ok for testing but not realistic in reality.

"""
import networking as net

# define the address at which the server listen and the clients connect to
server_address = "127.0.0.1", 5000

# Only log errors
net.Logging.logger.setLevel(40)


def main():
    # open and start the server and close afterwards
    with net.ClientManager(server_address, ClientCommunicator):
        # Connect a client to the server
        ServerCommunicator.connect(server_address, blocking=True, timeout=2)

        # Call functions at the server and print the return values
        ret = ServerCommunicator.remote_functions.greet_client()
        print(ret)

        ret = ServerCommunicator.remote_functions.say_hello("Doris")
        print(ret)

        ServerCommunicator.remote_functions.set_username("Jack")

        # Close the connection to the server at client-side
        ServerCommunicator.close_connection()


class ClientFunctions(net.ClientFunctions):
    # A class that defines every method that can be called at a client from the server
    @staticmethod
    def greet_server():
        return ServerCommunicator.remote_functions.say_hello("Walter")

    @staticmethod
    def say_hello(name: str) -> str:
        return f"Client: Hello {name}"


class ServerFunctions(net.ServerFunctions):
    # A class that defines every method that can be called at the server from a client
    @staticmethod
    def greet_client():
        return net.ClientPool.get().remote_functions.say_hello("Walter")

    @staticmethod
    def say_hello(name: str) -> str:
        return f"Server: Hello {name}"

    @staticmethod
    def set_username(name: str):
        net.ClientPool.get().username = name
        print(f"Successfully set username to '{net.ClientPool.get().username}'")


class ClientCommunicator(net.ClientCommunicator):
    # Server-side class that sets the available functions and make them available for communication
    local_functions = ServerFunctions
    remote_functions = ClientFunctions


class ServerCommunicator(net.ServerCommunicator):
    # Client-side class that sets the available functions and make them available for communication
    local_functions = ClientFunctions
    remote_functions = ServerFunctions


if __name__ == '__main__':
    main()
