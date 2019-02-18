import unittest
import time
import threading

from thread_testing import get_num_non_dummy_threads, wait_till_joined, wait_till_condition

from Communication_client import ServerCommunicator, MultiServerCommunicator, ServerFunctions
from Communication_server import ClientManager
from Communication_general import Communicator
from Logging import logger

dummy_address = ("127.0.0.1", 5000)


def clean_start(func):
    def wrapper(*args, **kwargs):
        DummyMultiServerCommunicator.close_all_connections()
        DummyServerCommunicator.close_connection()
        ret_value = func(*args, **kwargs)
        return ret_value
    return wrapper


class TestConnecting(unittest.TestCase):

    @clean_start
    def test_single_client_connect(self):
        DummyServerCommunicator.connect(dummy_address, time_out=1)
        self.assertIsInstance(DummyServerCommunicator.functions.__getattr__("communicator"), Communicator)

    @clean_start
    def test_multi_client_connect(self):
        DummyMultiServerCommunicator(0).connect(dummy_address, time_out=1)
        self.assertIsInstance(DummyMultiServerCommunicator(0).functions.__getattr__("communicator"), Communicator)
        DummyMultiServerCommunicator(1).connect(dummy_address, time_out=1)
        self.assertIsInstance(DummyMultiServerCommunicator(1).functions.__getattr__("communicator"), Communicator)

    @clean_start
    def test_single_client(self):
        with ClientManager(dummy_address) as listener:
            DummyServerCommunicator.connect(dummy_address)

            wait_till_condition(lambda: len(listener.clients) == 1, timeout=1)

            self.assertEqual(len(listener.clients), 1)
            self.assertEqual(get_num_non_dummy_threads(), 4)  # Main, listener, client_communicator, server_communicator
            self.assertEqual(listener.clients[0]._socket_connection.getpeername(),
                             DummyServerCommunicator.communicator._socket_connection.getsockname())

            DummyServerCommunicator.close_connection()
            wait_till_joined(DummyServerCommunicator.communicator, timeout=1)
            wait_till_condition(lambda: len(listener.clients.values()) == 0, timeout=1)
            # wait_till_condition(lambda: get_num_non_dummy_threads() == 2)

            self.assertEqual(get_num_non_dummy_threads(), 2)  # Main, listener
        wait_till_joined(listener)

        self.assertEqual(get_num_non_dummy_threads(), 1)

    @clean_start
    def test_multiple_clients(self):
        with ClientManager(dummy_address) as listener:
            DummyMultiServerCommunicator(0).connect(dummy_address)
            DummyMultiServerCommunicator(1).connect(dummy_address)

            wait_till_condition(lambda: len(listener.clients) == 2, timeout=2)

            self.assertEqual(len(listener.clients), 2)

            self.assertEqual(get_num_non_dummy_threads(), 6)
            # Main, listener, 2 * client_communicator, 2 * server_communicator
            self.assertEqual(listener.clients[0]._socket_connection.getpeername(),
                             DummyMultiServerCommunicator(0).communicator._socket_connection.getsockname())
            self.assertEqual(listener.clients[1]._socket_connection.getpeername(),
                             DummyMultiServerCommunicator(1).communicator._socket_connection.getsockname())

            DummyMultiServerCommunicator(0).close_connection()
            DummyMultiServerCommunicator(1).close_connection()

            wait_till_joined(DummyMultiServerCommunicator(0).communicator, timeout=2)
            wait_till_joined(DummyMultiServerCommunicator(1).communicator, timeout=2)
            wait_till_condition(lambda: len(listener.clients.values()) == 0, timeout=2)
            self.assertEqual(get_num_non_dummy_threads(), 2)  # Main, listener
        wait_till_joined(listener, timeout=1)

        self.assertEqual(get_num_non_dummy_threads(), 1)

    @clean_start
    def test_offline_server(self):
        connected = DummyServerCommunicator.connect(dummy_address, time_out=2)
        self.assertEqual(get_num_non_dummy_threads(), 1)
        self.assertEqual(connected, False)

    @clean_start
    def test_server_turn_on(self):
        DummyServerCommunicator.connect(dummy_address, blocking=False)
        with ClientManager(dummy_address) as listener:
            wait_till_condition(lambda: len(listener.clients) == 1, timeout=2)
            self.assertEqual(len(listener.clients), 1)
            DummyServerCommunicator.close_connection()
            wait_till_joined(DummyServerCommunicator.communicator, timeout=2)
            wait_till_condition(lambda: len(listener.clients) == 0, timeout=2)
            self.assertEqual(len(listener.clients), 0)
        self.assertEqual(get_num_non_dummy_threads(), 1)

    @clean_start
    def test_listener_clients(self):
        with ClientManager(dummy_address) as listener:
            self.assertEqual(len(listener.clients.values()), 0)
            DummyServerCommunicator.connect(dummy_address)
            wait_till_condition(lambda: len(listener.clients) == 1, timeout=2)
            self.assertEqual(len(listener.clients.values()), 1)
            DummyServerCommunicator.close_connection()
            wait_till_condition(lambda: len(listener.clients) == 0, timeout=2)
            self.assertEqual(len(listener.clients.values()), 0)


class TestCommunicator(unittest.TestCase):
    pass


class TestClientCommunicator(unittest.TestCase):

    def test_connection_single(self):

        DummyServerCommunicator.connect(dummy_address)
        self.assertIsInstance(ServerCommunicator.communicator, Communicator)
        self.assertIsInstance(DummyServerCommunicator.communicator, Communicator)

        DummyServerCommunicator.close_connection()
        self.assertIsInstance(ServerCommunicator.communicator, type(None))
        self.assertIsInstance(DummyServerCommunicator.communicator, type(None))

    def test_functions_communicator(self):
        DummyMultiServerCommunicator(0).connect(dummy_address)
        DummyMultiServerCommunicator(0).functions.dummy_function()


class TestNewConnectionListener(unittest.TestCase):

    def test_open_close(self):
        listener = ClientManager(dummy_address)
        listener.start()
        listener.stop_listening()
        self.assertEqual(listener._is_on, False)

    def test_context_guard(self):
        with ClientManager(dummy_address) as listener:
            self.assertEqual(listener._is_on, True)
            DummyServerCommunicator.connect(dummy_address)
            DummyServerCommunicator.close_connection()
        self.assertEqual(listener._is_on, False)
        self.assertEqual(threading.active_count(), 1)

    def test_single_connection(self):
        with ClientManager(dummy_address):
            DummyMultiServerCommunicator(0).connect(dummy_address)

            time.sleep(1)   # provides a clearer output, but also works without
            self.assertEqual(threading.active_count(), 4)

            DummyMultiServerCommunicator(0).close_connection()

        self.assertEqual(threading.active_count(), 1)

    def test_multiple_connections(self):
        with ClientManager(dummy_address):
            DummyMultiServerCommunicator(0).connect(dummy_address)
            DummyMultiServerCommunicator(1).connect(dummy_address)

            time.sleep(1)  # provides a clearer output, but also works without
            self.assertEqual(threading.active_count(), 6)

            DummyMultiServerCommunicator(0).close_connection()
            DummyMultiServerCommunicator(1).close_connection()

        self.assertEqual(threading.active_count(), 1)


class DummyServerCommunicator(ServerCommunicator):
    class _DummyServerFunctions(ServerFunctions):
        from networking_example.example_dummy_functions import dummy_no_arg_no_ret
        pass

    functions = _DummyServerFunctions


class DummyMultiServerCommunicator(MultiServerCommunicator):
    class _DummyServerFunctions(ServerFunctions):
        from networking_example.example_dummy_functions import dummy_no_arg_no_ret
        pass

    functions = _DummyServerFunctions


if __name__ == '__main__':
    unittest.main()
