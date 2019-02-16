import unittest

from networking.Communication_new import *


class TestCommunicator(unittest.TestCase):
    pass


class TestServerCommunicator(unittest.TestCase):

    def test_connection(self):
        addr = ("127.0.0.1", 5000)
        DummyServerCommunicator.connect(addr)
        DummyServerCommunicator.close_connection()
        self.assertIsInstance(ServerCommunicator.communicator, Communicator)
        self.assertIsInstance(DummyServerCommunicator.communicator, Communicator)


if __name__ == '__main__':
    unittest.main()
