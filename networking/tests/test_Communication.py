import unittest
import time
import threading

from thread_testing import get_num_non_dummy_threads, wait_till_joined, wait_till_condition

from Communication_client import ServerCommunicator, MultiServerCommunicator, ServerFunctions
from Communication_server import ClientManager
from Communication_general import Communicator
from Packets import FunctionPacket
from Logging import logger
from networking_example.example_dummy_functions import called

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
        self.assertIsInstance(DummyServerCommunicator.functions().__getattr__("communicator"), Communicator)

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


class TestCommunicating(unittest.TestCase):

    def test_send_function_add(self):
        with ClientManager(dummy_address) as listener:
            DummyServerCommunicator.connect(dummy_address)
            self.assertEqual(called, False)
            packet_sent = FunctionPacket("not", 10, name="John")
            DummyServerCommunicator.communicator.send_packet(packet_sent)
            wait_till_condition(lambda: len(listener.clients[0]._packets) == 1, timeout=2)
            packet_recv = listener.clients[0]._packets[0]
            self.assertEqual(packet_recv, packet_sent)
            DummyServerCommunicator.close_connection()

    def test_send_function_execute_return(self):
        self.assertEqual(called, False)
        with ClientManager(dummy_address) as listener:
            DummyServerCommunicator.connect(dummy_address)
            ret_value = DummyServerCommunicator.functions(timeout=2).dummy_no_arg_no_ret()
            self.assertEqual(ret_value, None)
            self.assertEqual(called, True)

    def test_functions_no_connection(self):
        self.assertRaises(ConnectionError, DummyServerCommunicator.functions(timeout=1).dummy_no_arg_no_ret)

    def test_functions_timeout(self):
        # May fail if packets are handled at server is implemented
        with ClientManager(dummy_address):
            DummyServerCommunicator.connect(dummy_address)
            ret = DummyServerCommunicator.functions(timeout=0).dummy_no_arg_no_ret()
            self.assertIsInstance(ret, TimeoutError)
            DummyServerCommunicator.close_connection()


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
