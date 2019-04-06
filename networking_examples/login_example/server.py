import interface
import pynetworking as net
import time


def request_login():
    username = net.ClientManager().get().remote_functions.get_username()
    password = net.ClientManager().get().remote_functions.get_password()
    return is_valid_data(username, password)


def is_valid_data(username, password):
    # This function just simulates a possible database access and validation
    if len(username) > 4 and len(password) > 4:
        return True
    return False


if __name__ == '__main__':
    address = ("127.0.0.1", 5000)
    client_manager = net.ClientManager(address, interface.ClientCommunicator)
    client_manager.start()
    time.sleep(20)
    client_manager.stop_listening()
    client_manager.stop_connections()
