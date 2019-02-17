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
            self.functions.__setattr__(self.functions, "communicator", self.communicator)
            self.communicator.start()


class ServerFunctions(metaclass=MetaFunctionCommunicator):
    communicator = None


# *******************************************************
# Start only for Testing
# *******************************************************


class DummyServerCommunicator(ServerCommunicator):
    class _DummyServerFunctions(ServerFunctions):
        from networking.tests.test_Communication import dummy_function
        pass

    functions = _DummyServerFunctions


class DummyMultiServerCommunicator(MultiServerCommunicator):
    class _DummyServerFunctions(ServerFunctions):
        from networking.tests.test_Communication import dummy_function
        pass

    functions = _DummyServerFunctions

# *******************************************************
# End only for Testing
# *******************************************************
