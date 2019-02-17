"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from networking.Logging import logger
from networking.Communication_general import Communicator, Connector, MultiConnector, MetaFunctionCommunicator


class ServerCommunicator(Connector):

    @staticmethod
    def connect(addr):
        if Connector.communicator is None:
            Connector.communicator = Communicator(addr)
            Connector.communicator.start()


class MultiServerCommunicator(MultiConnector):

    def connect(self, addr):
        if self.communicator is None:
            self.communicator = Communicator(addr, id_=self._id)
            self.communicator.start()


class ServerFunctions(metaclass=MetaFunctionCommunicator):
    pass


# *******************************************************
# Start only for Testing
# *******************************************************


class DummyServerCommunicator(ServerCommunicator):
    class _DummyServerFunctions(ServerFunctions):
        from networking import Packets
        pass

    functions = _DummyServerFunctions


class DummyMultiServerCommunicator(MultiServerCommunicator):
    class _DummyServerFunctions(ServerFunctions):
        from networking import Packets
        pass

    functions = _DummyServerFunctions

# *******************************************************
# End only for Testing
# *******************************************************
