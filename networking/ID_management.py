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
@TODO_: Adjust docstrings
"""
from typing import List, Optional, Dict, Tuple
from Logging import logger

from Packets import FunctionPacket, DataPacket, Packet

__all__ = ["IDManager", "remove_manager"]


class IDManagers(type):
    """Each Communicator has its own ID. With this ID it gets its appropriate IDManager"""
    _instances: Dict[int, 'IDManager'] = {}

    def __call__(cls, *args, **kwargs):
        id_ = args[0]
        if id_ not in cls._instances:
            cls._instances[id_] = super(IDManagers, cls).__call__(id_)
        return cls._instances[id_]

    @staticmethod
    def remove(id_):
        IDManagers._instances.pop(id_)


class IDManager(metaclass=IDManagers):

    def __init__(self, id_: int) -> None:
        self.id = id_
        self._next_function_id = 0
        self._next_outer_id = 0
        self._function_stack: List[int] = []

    def set_ids_of_packet(self, packet: Packet) -> Optional[Packet]:
        outer_id = self._next_outer_id
        if isinstance(packet, FunctionPacket):
            func_id = self._is_function_packet()
        elif isinstance(packet, DataPacket):
            func_id = self._is_data_packet()
        else:
            logger.error("Unknown packet_class (%s)", type(packet).__name__)
            return None

        packet.set_ids(func_id, outer_id)
        self._next_outer_id += 1
        return packet

    def update_ids_by_packet(self, packet: Packet) -> None:
        self._next_outer_id = packet.header.id_container.outer_id
        if isinstance(packet, FunctionPacket):
            self._is_function_packet()
        elif isinstance(packet, DataPacket):
            self._is_data_packet()
        else:
            logger.error("Unknown packet_class (%s)", type(packet).__name__)

    def get_next_outer_id(self) -> int:
        return self._next_outer_id

    def _is_function_packet(self) -> int:
        self._function_stack.append(self._next_function_id)
        function_id = self._next_function_id

        self._next_function_id += 1
        return function_id

    def _is_data_packet(self) -> int:
        pass

    def get_next_ids(self) -> Tuple[int, int]:
        return self._next_function_id, self._next_outer_id

    def get_function_stack(self) -> List[int]:
        return self._function_stack


def remove_manager(id_: int) -> None:
    """Called when a communicator is stopped. So its ID Manager isn´t needed anymore"""
    try:
        IDManagers.remove(id_)
    except KeyError:
        pass
