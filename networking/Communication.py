"""
@author: Julian Sobott
@created: 25.09.2018
@brief: Main File for Communication functions
@description:

@use:
"""
import threading
import socket
import time
import os

from networking.Data import Packet, File_meta_packet, Data_packet, Function_packet, Status_packet
from networking.ID_management import IDManager, remove_manager
from networking.Logging import logger


class Communicator(threading.Thread):

    CHUNK_SIZE = 1048

    def __init__(self, tcp_connection, address, id_, public_functions, is_connected=False):
        super().__init__(name="Communicator_thread_" + str(id_))
        self.ID = id_
        self.address = address
        self.tcp_connection = tcp_connection
        self.packet_list = []
        self.public_functions = public_functions
        self.is_on = True
        self.is_paused = False
        self.is_connected = False
        self.is_connected = is_connected

    def run(self):
        if not self.is_connected:
            self.reconnect()
        self.wait_for_new_input()

    def send_packet(self, packet):
        try:
            IDManager(self.ID).set_ids_of_packet(packet)
            send_data = packet.pack()
            self.tcp_connection.send(send_data)
            self.is_connected = True
        except OSError:
            logger.error("Could not send packet: %s", str(packet))

    def send_file(self, file_path):
        file_meta_packet = File_meta_packet(file_path)
        self.send_packet(file_meta_packet)
        file_content_size = self.CHUNK_SIZE - Data_packet.get_empty_size("FILE_DATA")

        with open(file_path, "rb") as file:
            file_data = file.read(file_content_size)
            while file_data:
                data_packet = Data_packet("FILE_DATA", file_data)
                self.send_packet(data_packet)
                file_data = file.read(file_content_size)

    def receive_file(self, save_path):
        """:return local_file_path at success and None at failure"""
        file_meta_packet = self.wait_for_response((File_meta_packet, Status_packet))
        if file_meta_packet is None:
            self.stop()
            return None
        if isinstance(file_meta_packet, Status_packet):
            return None
        if os.path.isdir(save_path):
            file_path = os.path.join(save_path, file_meta_packet.file_name)
        else:
            file_path = save_path
        file_size = file_meta_packet.size
        received = 0
        with open(file_path, "bw+") as file:
            while received < file_size:
                data_packet = self.wait_for_response(Data_packet)
                content = data_packet.data[0]
                file.write(content)
                received += len(content)
        return file_path

    def get_file(self, fil_path_at_other, save_path):
        """:return local_file_path at success and None at failure"""
        function_packet = Function_packet(self.public_functions.return_file, fil_path_at_other)
        self.send_packet(function_packet)
        response = self.receive_file(save_path)
        return response

    def wait_for_response(self, packet_type=None):
        """Need to be called at each end of function to validate success"""
        DEBUG_PRINTED_WAIT = False
        DEBUG_PRINTED_LOSS = False
        while self.is_on:
            handled_packet = False
            next_outer_id = IDManager(self.ID).get_next_outer_id()
            if not DEBUG_PRINTED_WAIT:
                #logger.debug("Wait for packet: %d", next_outer_id)
                DEBUG_PRINTED_WAIT = True
            for packet in self.packet_list:
                if packet.id_container.outer_id == next_outer_id:
                    DEBUG_PRINTED_WAIT = False
                    DEBUG_PRINTED_LOSS = False
                    handled_packet = True
                    if packet_type and not isinstance(packet, packet_type):
                        logger.info("Expected: %s, but received: %s",
                                    str(packet_type.__name__), str(type(packet).__name__))
                    IDManager(self.ID).update_ids_by_packet(packet)
                    self.packet_list.remove(packet)
                    if isinstance(packet, Function_packet):
                        # logger.debug("Execute function packet")
                        self.execute_packet(packet)
                        if not packet_type or isinstance(packet, packet_type):
                            return
                    elif isinstance(packet, Data_packet):
                        return packet
                    elif isinstance(packet, Status_packet):
                        # TODO: handle handle at client or server
                        return packet
                    break
            if not DEBUG_PRINTED_LOSS and not handled_packet and len(self.packet_list) > 0:
                #logger.error("Packet loss! Missing packet with outer_id: %d", next_outer_id)
                DEBUG_PRINTED_LOSS = True
            time.sleep(0.3)

    def execute_packet(self, packet):
        packet.execute(self, self.public_functions)

    def wait_for_new_input(self):

        while self.is_on and self.is_connected:
            while self.is_paused:
                time.sleep(1)
            try:
                chunk_data = self.tcp_connection.recv(self.CHUNK_SIZE)
                try:
                    packet, extra_bytes = Packet.unpack(chunk_data)
                    if len(extra_bytes) > 0:
                        logger.debug("Extra bytes: %s", extra_bytes)
                    # logger.debug("%s", str(packet))
                    self.packet_list.append(packet)
                except ValueError as e:
                    if len(chunk_data) == 0:
                        self.stop()
                        logger.warning("Server connection closed")
                    if chunk_data is not None:
                        logger.error("%s\nwith Chunk-data: %s", str(e), str(chunk_data))

            except ConnectionResetError:
                logger.error("Connection reset, (%s)", str(self.address))
                self.stop()

            except ConnectionAbortedError:
                logger.error("Connection aborted, (%s)", str(self.address))
                self.stop()

            except OSError:
                logger.error("TCP connection closed while listening")
                self.stop()

    def reconnect(self, address=None, pause=2, timeout=-1):
        waited = 0

        while self.is_on and not self.is_connected:
            try:
                # TODO: Add handshake
                self.tcp_connection.send(b"")
                self.is_connected = True
            except OSError:
                addr = self.address if address is None else address
                try:
                    self.tcp_connection.connect(addr)
                except ConnectionRefusedError:
                    logger.warning("Could not connect to server with address: (%s)", str(addr))

                except OSError as e:
                    logger.error("Is already connected to server")
                    logger.debug(e)

            time.sleep(1)
            waited += pause
            if timeout != -1 and waited >= timeout:
                return

    def get_is_connected(self):
        if self.is_connected:
            return True
        else:
            time.sleep(2)   # wait if thread connects while waiting
            # TODO: Maybe use another thread (connection_failed)
            if self.is_connected:
                return True
            else:
                return False

    def stop(self):
        self.is_on = False
        self.is_connected = False
        self.tcp_connection.close()
        remove_manager(self.ID)

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False


class Server:

    def __init__(self, public_functions, address):
        self.clients = []
        self.connection_listener = New_connection_listener(self, public_functions, address)
        self.next_id = 0

    def add_client(self, client):
        self.clients.append(client)

    def start(self):
        self.connection_listener.start()

    def stop(self):
        self.connection_listener.stop_connections()
        self.connection_listener.stop_listening()

    def get_next_client_id(self):
        self.next_id += 1
        return self.next_id


class New_connection_listener(threading.Thread):

    def __init__(self, server, public_functions, address):
        super().__init__(name="connection_listener")
        self.thread_ID = 1001
        self.tcp_server = socket.socket()
        self.is_on = True   # Final
        self.is_paused = False  # Temporary
        self.server = server
        self.public_functions = public_functions
        self.address = address

    def run(self):
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_server.bind(self.address)
        logger.debug("Server is now listening on: %s:%d", self.address[0], self.address[1])
        while self.is_on:
            while self.is_paused:
                time.sleep(1)

            self.tcp_server.listen(4)
            try:
                (conn, addr) = self.tcp_server.accept()
                logger.info("New client connected: (%s)", str(addr))
            except OSError:
                logger.error("TCP connection closed while listening")

            client = Communicator(conn, addr, self.server.get_next_client_id(), self.public_functions, is_connected=True)
            client.start()
            self.server.add_client(client)

    def stop_listening(self):
        self.is_on = False
        self.tcp_server.close()
        logger.info("Closed server listener")

    def stop_connections(self):
        for t in self.server.clients:
            t.join()


class Public_communicator:

    def send_packet(self, packet):
        return self.communicator.send_packet(packet)

    def send_file(self, file_path):
        return self.communicator.send_file(file_path)

    def send_status_packet(self, success, packet=None, text=""):
        if packet:
            send_packet = packet
        else:
            if success:
                send_packet = Status_packet(Status_packet.Status_code.successful, text)
            else:
                send_packet = Status_packet(Status_packet.Status_code.failed, text)
        self.send_packet(send_packet)

    def receive_file(self, save_path):
        return self.communicator.receive_file(save_path)

    def get_file(self, file_path_at_other, save_path):
        return self.communicator.get_file(file_path_at_other, save_path)

    def wait_for_response(self, packet_type=None):
        return self.communicator.wait_for_response(packet_type)

    def stop(self):
        self.communicator.stop()

    def is_connected(self):
        return self.communicator.get_is_connected()

    def _execute_packet(self, packet):
        return packet.execute(self, self.communicator.public_functions)


class Client(Public_communicator):

    def __init__(self, server_addr, public_functions):
        tcp_connection = socket.socket()
        self.communicator = Communicator(tcp_connection, server_addr, 0, public_functions)
        self.communicator.execute_packet = self._execute_packet
        self.communicator.start()


class Server_client(Public_communicator):

    def __init__(self, client_id, communicator):
        self.ID = client_id
        self.communicator = communicator
        self.communicator.execute_packet = self._execute_packet






