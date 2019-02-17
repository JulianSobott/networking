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

    def test_connection(self):

        DummyServerCommunicator.connect(dummy_address)
        self.assertIsInstance(ServerCommunicator.communicator, Communicator)
        self.assertIsInstance(DummyServerCommunicator.communicator, Communicator)

        DummyServerCommunicator.close_connection()
        self.assertIsInstance(ServerCommunicator.communicator, type(None))
        self.assertIsInstance(DummyServerCommunicator.communicator, type(None))


class TestNewConnectionListener(unittest.TestCase):

    def test_open_close(self):
        listener = NewConnectionListener(dummy_address)
        listener.start()
        listener.stop_listening()
        self.assertEqual(listener._is_on, False)

    def test_single_connection(self):
        listener = NewConnectionListener(dummy_address)
        listener.start()
        DummyMultiServerCommunicator(0).connect(dummy_address)

        time.sleep(1)   # provides a clearer output, but also works without
        self.assertEqual(threading.active_count(), 4)

        DummyMultiServerCommunicator(0).close_connection()
        listener.stop_listening()
        listener.stop_connections()

        self.assertEqual(threading.active_count(), 1)

    def test_multiple_connections(self):
        listener = NewConnectionListener(dummy_address)
        listener.start()
        DummyMultiServerCommunicator(0).connect(dummy_address)
        DummyMultiServerCommunicator(1).connect(dummy_address)

        time.sleep(1)  # provides a clearer output, but also works without
        self.assertEqual(threading.active_count(), 6)

        DummyMultiServerCommunicator(0).close_connection()
        DummyMultiServerCommunicator(1).close_connection()

        listener.stop_listening()
        listener.stop_connections()

        self.assertEqual(threading.active_count(), 1)


if __name__ == '__main__':
    unittest.main()
