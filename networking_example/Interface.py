"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net
from Server import dummy_func


class Meta(type):

    def __getattribute__(self, item):
        # =====not necessary========
        try:
            func = type.__getattribute__(self, item)
        except AttributeError:
            pass

        # =====necessary========
        def container(*args):
            function_name = item
            function_args = args
            # send function packet
            # recv data packet
            # unpack data packet
            data = None
            return data
        return container


class Parent(metaclass=Meta):

    @classmethod
    def connect(cls, addr):
        net.ServerCommunicator(addr)


class ServerCommunicator(Parent):
    from Server import dummy_func


