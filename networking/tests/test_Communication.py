import unittest
import sys

from thread_testing import get_num_non_dummy_threads, wait_till_joined, wait_till_condition

from Communication_client import ServerCommunicator, MultiServerCommunicator, ServerFunctions
from Communication_server import ClientManager, ClientFunctions, ClientCommunicator, MetaClientManager
from Communication_general import Communicator, Connector, to_server_id
from Packets import FunctionPacket
from Logging import logger

dummy_address = ("127.0.0.1", 5000)


class CommunicationTestCase(unittest.TestCase):
    def tearDown(self):
        DummyServerCommunicator.close_connection()
        MultiServerCommunicator.close_all_connections()
        MetaClientManager.tear_down()

    def setUp(self):
        DummyMultiServerCommunicator.close_all_connections()
        DummyServerCommunicator.close_connection()


class StdOutEqualizer:

    def __init__(self, test_case, expected):
        self.test_case: CommunicationTestCase = test_case
        self.expected = expected
        self.original = sys.stdout
        self.file_path = "std_out.txt"

    def __enter__(self):
        self.original = sys.stdout
        sys.stdout = open(self.file_path, "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self.original
        with open(self.file_path, "r") as std_out:
            self.test_case.assertEqual(self.expected, std_out.read().strip())


class TestConnecting(CommunicationTestCase):

    def test_single_client_connect(self):
        DummyServerCommunicator.connect(dummy_address, time_out=0)

        self.assertEqual(DummyServerCommunicator.remote_functions.__getattr__("_connector"), DummyServerCommunicator)
        self.assertEqual(DummyServerCommunicator.remote_functions().__getattr__("_connector"), DummyServerCommunicator)
        self.assertEqual(DummyServerCommunicator.remote_functions, DummyServerCommunicator.remote_functions())

    def test_multi_client_connect(self):
        DummyMultiServerCommunicator(0).connect(dummy_address, time_out=0)
        self.assertIsInstance(DummyMultiServerCommunicator(0).remote_functions.__getattr__("_connector"),
                              DummyMultiServerCommunicator)
        DummyMultiServerCommunicator(1).connect(dummy_address, time_out=0)
        self.assertIsInstance(DummyMultiServerCommunicator(1).remote_functions.__getattr__("_connector"),
                              DummyMultiServerCommunicator)

    def test_single_client(self):
        with ClientManager(dummy_address, DummyClientCommunicator) as listener:
            DummyServerCommunicator.connect(dummy_address)

            wait_till_condition(lambda: len(listener.clients) == 1, timeout=1)

            self.assertEqual(len(listener.clients), 1)
            self.assertEqual(get_num_non_dummy_threads(), 4)  # Main, listener, client_communicator, server_communicator
            self.assertEqual(listener.clients[to_server_id(0)].communicator._socket_connection.getpeername(),
                             DummyServerCommunicator.communicator._socket_connection.getsockname())

            DummyServerCommunicator.close_connection()
            wait_till_joined(DummyServerCommunicator.communicator, timeout=1)
            wait_till_condition(lambda: len(listener.clients.values()) == 0, timeout=1)
            # wait_till_condition(lambda: get_num_non_dummy_threads() == 2)

            self.assertEqual(get_num_non_dummy_threads(), 2)  # Main, listener
        wait_till_joined(listener)

        self.assertEqual(get_num_non_dummy_threads(), 1)

    def test_multiple_clients(self):
        with ClientManager(dummy_address, DummyClientCommunicator) as listener:
            DummyMultiServerCommunicator(0).connect(dummy_address)
            DummyMultiServerCommunicator(1).connect(dummy_address)

            wait_till_condition(lambda: len(listener.clients) == 2, timeout=2)

            self.assertEqual(len(listener.clients), 2)

            self.assertEqual(get_num_non_dummy_threads(), 6)
            # Main, listener, 2 * client_communicator, 2 * server_communicator
            self.assertEqual(listener.clients[to_server_id(0)].communicator._socket_connection.getpeername(),
                             DummyMultiServerCommunicator(0).communicator._socket_connection.getsockname())
            self.assertEqual(listener.clients[to_server_id(1)].communicator._socket_connection.getpeername(),
                             DummyMultiServerCommunicator(1).communicator._socket_connection.getsockname())

            DummyMultiServerCommunicator(0).close_connection()
            DummyMultiServerCommunicator(1).close_connection()

            wait_till_joined(DummyMultiServerCommunicator(0).communicator, timeout=2)
            wait_till_joined(DummyMultiServerCommunicator(1).communicator, timeout=2)
            wait_till_condition(lambda: len(listener.clients.values()) == 0, timeout=2)
            self.assertEqual(get_num_non_dummy_threads(), 2)  # Main, listener
        wait_till_joined(listener, timeout=1)

        self.assertEqual(get_num_non_dummy_threads(), 1)

    def test_offline_server(self):
        connected = DummyServerCommunicator.connect(dummy_address, time_out=2)
        self.assertEqual(get_num_non_dummy_threads(), 1)
        self.assertEqual(connected, False)

    def test_server_turn_on(self):
        DummyServerCommunicator.connect(dummy_address, blocking=False)
        with ClientManager(dummy_address, DummyClientCommunicator) as listener:
            wait_till_condition(lambda: len(listener.clients) == 1, timeout=2)
            self.assertEqual(len(listener.clients), 1)
            DummyServerCommunicator.close_connection()
            wait_till_joined(DummyServerCommunicator.communicator, timeout=2)
            wait_till_condition(lambda: len(listener.clients) == 0, timeout=2)
            self.assertEqual(len(listener.clients), 0)
        self.assertEqual(get_num_non_dummy_threads(), 1)

    def test_listener_clients(self):
        with ClientManager(dummy_address, DummyClientCommunicator) as listener:
            self.assertEqual(len(listener.clients.values()), 0)
            DummyServerCommunicator.connect(dummy_address)
            wait_till_condition(lambda: len(listener.clients) == 1, timeout=2)
            self.assertEqual(len(listener.clients.values()), 1)
            DummyServerCommunicator.close_connection()
            wait_till_condition(lambda: len(listener.clients) == 0, timeout=2)
            self.assertEqual(len(listener.clients.values()), 0)


class TestCommunicating(CommunicationTestCase):

    def test_send_function_add(self):
        with ClientManager(dummy_address, DummyClientCommunicator) as listener:
            DummyServerCommunicator.connect(dummy_address)
            packet_sent = FunctionPacket("not", 10, name="John")
            DummyServerCommunicator.communicator.send_packet(packet_sent)
            wait_till_condition(lambda: len(listener.clients[to_server_id(0)].communicator._packets) == 1, timeout=2)
            packet_recv = listener.clients[to_server_id(0)].communicator._packets[0]
            self.assertEqual(packet_recv, packet_sent)

    def test_send_function_execute_return(self):
        with ClientManager(dummy_address, DummyClientCommunicator) as listener:
            DummyServerCommunicator.connect(dummy_address)
            ret_value = None
            logger.debug(listener.clients[to_server_id(0)].local_functions)
            logger.debug(DummyClientCommunicator.local_functions)
            try:
                with StdOutEqualizer(self, "Dummy function called"):
                    ret_value = DummyServerCommunicator.remote_functions(timeout=2).dummy_no_arg_no_ret()
            except TimeoutError:
                pass
            self.assertEqual(ret_value, None)

    def test_functions_no_connection(self):
        self.assertRaises(ConnectionError, DummyServerCommunicator.remote_functions(timeout=0).dummy_no_arg_no_ret)

    def test_functions_timeout(self):
        # May fail if packets are handled at server is implemented
        with ClientManager(dummy_address, DummyClientCommunicator):
            DummyServerCommunicator.connect(dummy_address)
            self.assertRaises(TimeoutError, DummyServerCommunicator.remote_functions(timeout=0).dummy_no_arg_no_ret)

    def test_function_args(self):
        with ClientManager(dummy_address, DummyClientCommunicator):
            DummyServerCommunicator.connect(dummy_address)

            ret_value = DummyServerCommunicator.remote_functions(timeout=2).dummy_args_ret("Bunny")
            self.assertEqual((10, 10), ret_value)


class _DummyServerFunctions(ServerFunctions):
    from networking.tests.example_functions import immutable_args_ret, no_arg_ret
    # def dummy_no_arg_no_ret(self) -> bool: ...


class _DummyClientFunctions(ClientFunctions):
    from networking.tests.example_functions import immutable_args_ret, no_arg_ret


class DummyServerCommunicator(ServerCommunicator):
    remote_functions = _DummyServerFunctions
    local_functions = _DummyClientFunctions


class DummyMultiServerCommunicator(MultiServerCommunicator):
    remote_functions = _DummyServerFunctions
    local_functions = _DummyClientFunctions


class DummyClientCommunicator(ClientCommunicator):
    remote_functions = _DummyClientFunctions
    local_functions = _DummyServerFunctions


if __name__ == '__main__':
    unittest.main()
