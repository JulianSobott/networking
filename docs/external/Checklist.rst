New project checklist
======================

This page contains a checklist with all necessary parts that you need, when you start a new project. This checklist \
assumes you know how to use the library and just need a short recapitulation. If not check out the :any:`Getting_started` \
page.

1. :ref:`Install <Installation>` pynetworking
2. Override classes:
    2.1 ServerFunctions (:doc:`Functions`)

    2.2 ClientFunctions (:doc:`Functions`)

    2.3 ServerCommunicator (:class:`~pynetworking.Communication_client.ServerCommunicator`)

    2.4 ClientCommunicator (:class:`~pynetworking.Communication_server.ClientCommunicator`)

3. Start the server with :class:`~pynetworking.Communication_server.ClientManager`
4. Start the client with created :class:`~pynetworking.Communication_client.ServerCommunicator`

While you are working on your project, remember to add necessary functions to the :doc:`Functions`.


Minimal Code that can be copied
-----------------------------------

*net_interface.py*

.. code-block:: python

    import pynetworking as net


    class ServerFunctions(net.ServerFunctions):
        pass
        # Import all Server functions here
        # e.g. from server import function1


    class ClientFunctions(net.ClientFunctions):
        pass
        # Import all Client functions here
        # e.g. from client import function2


    class ServerCommunicator(net.ServerCommunicator):
        remote_functions = ServerFunctions
        local_functions = ClientFunctions


    class ClientCommunicator(net.ClientCommunicator):
        remote_functions = ClientFunctions
        local_functions = ServerFunctions

    #: alias for all server functions
    server = ServerCommunicator.remote_functions


    def get_client() -> ClientCommunicator:
        """Main purpose is to supply better auto completions"""
        return net.ClientManager().get()


*client.py*

.. code-block:: python

    import net_interface


    address = ("127.0.0.1", 5000)
    net_interface.ServerCommunicator.connect(address)
    # Do more stuff
    net_interface.ServerCommunicator.close_connection()


*server.py*

.. code-block:: python

    import net_interface
    import multiprocessing


    client_manager = net.ClientManager(address, net_interface.ClientCommunicator)
    client_manager.start()
    # Server is now started
    #: One possible way to add an option to stop the server
    queue = multiprocessing.Queue()
    try:
        while True:
            msg = queue.get()
            if msg == "stop":
                break
    finally:
        client_manager.stop_listening()
        client_manager.stop_connections()
