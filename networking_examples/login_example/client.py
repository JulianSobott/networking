import interface

server = interface.ServerCommunicator.remote_functions


def login():
    successfully_logged_in = server.request_login()
    if successfully_logged_in:
        print("Successfully logged in")
    else:
        print("Login failed")


def get_username():
    return input("Enter username: ")


def get_password():
    return input("Enter password: ")


if __name__ == '__main__':
    address = ("127.0.0.1", 5000)
    interface.ServerCommunicator.connect(address)
    login()
    # Do more stuff
    interface.ServerCommunicator.close_connection()
