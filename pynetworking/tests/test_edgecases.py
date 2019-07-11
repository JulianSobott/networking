"""

"""
import time
import unittest
import threading
from pynetworking import ClientManager, MultiServerCommunicator
from pynetworking.tests.example_functions import DummyServerCommunicator, DummyMultiServerCommunicator, \
    DummyClientCommunicator
from pynetworking.Logging import logger
from pynetworking import Communication_general

logger.setLevel(10)


class TestManyClients(unittest.TestCase):
    address = "127.0.0.1", 5000

    def setUp(self):
        self.manager = ClientManager(self.address, DummyClientCommunicator)
        self.manager.start()
        Communication_general.ENCRYPTED_COMMUNICATION = False

    def tearDown(self):
        DummyMultiServerCommunicator.close_all_connections()
        logger.debug(self.manager.clients)
        self.manager.stop_listening()
        self.manager.stop_connections()

    def test_many(self):
        clients = []
        thread_pool = []

        def client_exe(client: DummyMultiServerCommunicator):
            client.connect(self.address)
            c_id = client.remote_functions.return_client_id()
            print(c_id)
            client.close_connection()

        for i in range(2):
            clients.append(DummyMultiServerCommunicator(i))
            thread_pool.append(threading.Thread(target=client_exe, args=(clients[i],)))
            thread_pool[i].start()
            time.sleep(0.1)

        for t in thread_pool:
            t.join()
