import unittest
import time
import threading

from networking.Communication_Client import *
from networking.Communication_server import *
from networking.Communication_general import Communicator

dummy_address = ("127.0.0.1", 5000)


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
        listener = NewConnectionListener(dummy_address)
        listener.start()
        listener.stop_listening()
        self.assertEqual(listener._is_on, False)

    def test_context_guard(self):
        with NewConnectionListener(dummy_address) as listener:
            self.assertEqual(listener._is_on, True)
            DummyServerCommunicator.connect(dummy_address)
            DummyServerCommunicator.close_connection()
        self.assertEqual(listener._is_on, False)
        self.assertEqual(threading.active_count(), 1)

    def test_single_connection(self):
        with NewConnectionListener(dummy_address):
            DummyMultiServerCommunicator(0).connect(dummy_address)

            time.sleep(1)   # provides a clearer output, but also works without
            self.assertEqual(threading.active_count(), 4)

            DummyMultiServerCommunicator(0).close_connection()

        self.assertEqual(threading.active_count(), 1)

    def test_multiple_connections(self):
        with NewConnectionListener(dummy_address):
            DummyMultiServerCommunicator(0).connect(dummy_address)
            DummyMultiServerCommunicator(1).connect(dummy_address)

            time.sleep(1)  # provides a clearer output, but also works without
            self.assertEqual(threading.active_count(), 6)

            DummyMultiServerCommunicator(0).close_connection()
            DummyMultiServerCommunicator(1).close_connection()

        self.assertEqual(threading.active_count(), 1)


def dummy_function():
    print("Dummy function called")


if __name__ == '__main__':
    unittest.main()
