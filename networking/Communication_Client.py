"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from networking.Logging import logger
from networking.Packets import DataPacket, FunctionPacket
from networking.Communication_general import Communicator


class MetaFunctionCommunicator(type):

    def __getattribute__(self, item):

        if item == "__getattr__":
            return type.__getattribute__(self, item)

        def container(*args, **kwargs):
            function_name = item
            # send function packet
            self._send_function(function_name, *args, **kwargs)
            # recv data packet
            data_packet = ServerCommunicator.communicator.wait_for_response(self._recv_function)
            # unpack data packet
            return_values = data_packet.data["return"]
            return return_values

        return container

    @staticmethod
    def _send_function(function_name, *args, **kwargs):
        packet = FunctionPacket(function_name, *args, **kwargs)
        ServerCommunicator.communicator.send_packet(packet)

    def _recv_function(cls, function_name, args, kwargs):
        try:
            func = type.__getattribute__(cls, function_name)
            try:
                ret_value = func(*args, **kwargs)
            except TypeError as e:
                ret_value = e
        except AttributeError as e:
            ret_value = e
        ret_kwargs = {"return": ret_value}
        data_packet = DataPacket(**ret_kwargs)
        ServerCommunicator.communicator: Communicator
        ServerCommunicator.communicator.send_packet(data_packet)

    def __getattr__(self, item):
        func = type.__getattribute__(self, item)
        return func


class ServerCommunicator:
    server_functions = None
    communicator = None

    @classmethod
    def connect(cls, addr):
        ServerCommunicator.communicator = Communicator(addr)
        ServerCommunicator.communicator.start()

    @staticmethod
    def close_connection():
        ServerCommunicator.communicator.stop()


# *******************************************************
# Start only for Testing
# *******************************************************
class ServerFunctions(metaclass=MetaFunctionCommunicator):
    pass


class DummyServerCommunicator(ServerCommunicator):
    class _DummyServerFunctions(ServerFunctions):
        from networking import Packets
        pass

    server_functions = _DummyServerFunctions

# *******************************************************
# End only for Testing
# *******************************************************
