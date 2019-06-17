New project checklist
======================

This page contains a checklist with all necessary parts that you need, when you start a new project. This checklist \
assumes you know how to use the library and just need a short recapitulation. If not check out the :any:`Getting_started` \
page.

1. :ref:`Install <Installation>` pynetworking
2. Overwrite classes:
    2.1 ServerFunctions (:doc:`Functions`)

    2.2 ClientFunctions (:doc:`Functions`)

    2.3 ServerCommunicator (:class:`~pynetworking.Communication_client.ServerCommunicator`)

    2.4 ClientCommunicator (:class:`~pynetworking.Communication_server.ClientCommunicator`)

3. Start the server with :class:`~pynetworking.Communication_server.ClientManager`
4. Start the client with created :class:`~pynetworking.Communication_client.ServerCommunicator`

While you are working on your project, remember to add necessary functions to the :doc:`Functions`.