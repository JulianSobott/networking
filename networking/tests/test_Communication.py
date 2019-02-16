import unittest

from networking.Communication_Client import *
from networking.Communication_server import *

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


if __name__ == '__main__':
    unittest.main()
