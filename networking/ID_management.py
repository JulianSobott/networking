"""
@author: Julian Sobott
@created: 13.11.2018
@brief: Handles ids for proper network communication
@description:
Each packet has 3 ids: func_id - inner_id - outer_id
func_id: increased for each new function. All Packets inside a function have same id
        #Which packet belongs to which function
inner_id: increased for each new packet inside a function
        #Not necessary but easier to debug (see num packets inside function)
outer_id: increased for each new packet.
        #See which packet is next. Watch packet loss

IDManagers is a metaclass to deliver multiple IDManagers for multiple Communicators

@external_use:
Call IDManager([ID]) to work with it.
ID is the ID of the communicator. (per client one ID)

When a communicator is closed call remove_manger(), with the communicator ID

@internal_use:

"""
from .Logging import logger

from .Packets import FunctionPacket, DataPacket, Status_packet

__all__ = ["IDManager", "remove_manager"]


class IDManagers(type):
    """Each Communicator has its own ID. With this ID it gets its appropriate IDManager"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        id_ = args[0]
        if id_ not in cls._instances:
            cls._instances[id_] = super(IDManagers, cls).__call__(id_)
        return cls._instances[id_]

    @classmethod
    def remove(mcs, id_):
        mcs._instances.pop(id_)


class IDManager(metaclass=IDManagers):

    def __init__(self, id_):
        self.id = id_
        self._function_id = 0
        self._inner_id = 0
        self._outer_id = 0
        self._function_stack = []   # [function_id, last_inner_id]

    def set_ids_of_packet(self, packet):
        self._outer_id += 1
        outer_id = self._outer_id
        if isinstance(packet, FunctionPacket):
            func_id, inner_id = self._is_function_packet()
        elif isinstance(packet, DataPacket):
            func_id, inner_id = self._is_data_packet()
        elif isinstance(packet, Status_packet):
            func_id, inner_id = self._is_status_packet(packet)
        else:
            logger.error("Unknown packet_class (%s)", type(packet).__name__)
            return

        packet.set_ids(func_id, inner_id, outer_id)
        return packet

    def update_ids_by_packet(self, packet):
        self._outer_id = packet.id_container.outer_id
        if isinstance(packet, FunctionPacket):
            self._is_function_packet()
        elif isinstance(packet, DataPacket):
            self._is_data_packet()
        elif isinstance(packet, Status_packet):
            self._is_status_packet(packet)
        else:
            logger.error("Unknown packet_class (%s)", type(packet).__name__)

    def get_next_outer_id(self):
        return self._outer_id + 1

    def _is_function_packet(self):
        self._function_id += 1
        self._inner_id = 1
        self._function_stack.append([self._function_id, self._inner_id])
        function_id = self._function_id
        inner_id = self._inner_id
        return function_id, inner_id

    def _is_data_packet(self):
        self._inner_id += 1
        self._function_stack[-1][1] = self._inner_id
        function_id = self._function_stack[-1][0]
        inner_id = self._function_stack[-1][1]
        return function_id, inner_id

    def _is_status_packet(self, packet):
        if packet.last_in_func:
            function_id, self._inner_id = self._function_stack.pop(-1)
        function_id = self._function_id
        inner_id = self._inner_id + 1
        return function_id, inner_id


def remove_manager(id_):
    """Called when a communicator is stopped. So its ID Manager isn´t needed anymore"""
    try:
        IDManagers.remove(id_)
    except KeyError:
        pass
