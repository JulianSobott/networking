Functions classes
=================

Every program needs to overwrite two classes: :class:`ServerFunctions` and :class:`ClientFunctions`.
Both inherit from the base class :class:`Functions`. These classes define which functions are callable from the remote side.

Usage examples:
---------------

.. _functions-version-1:

**Version 1: Both classes in one file**

*interface.py*

.. literalinclude:: ../../pynetworking_examples/client_interface_server/Interface.py
    :language: python
    :start-after: import pynetworking as net
    :end-before: class ServerCommunicator(net.ServerCommunicator):

.. _functions-version-2:

**Version 2: server and client files are split**

*Client.py*

.. code-block:: python

    class ServerFunctions(net.ServerFunctions):
        @staticmethod
        def dummy_function(x, y): ...

    class ClientFunctions(net.ServerFunctions):
        @staticmethod
        def client_function():
            return client.client_function()

*Server.py*

.. code-block:: python

    class ServerFunctions(net.ServerFunctions):
        @staticmethod
        def dummy_function(x, y):
            return server.dummy_function(x, y)

    class ClientFunctions(net.ServerFunctions):
        @staticmethod
        def client_function(): ...

.. _functions-version-2.1:

**Version 2.1: server and client files are split + mix 1 and 2**

*Client.py*

.. code-block:: python

    class ServerFunctions(net.ServerFunctions):
        @staticmethod
        def dummy_function(x, y): ...

    class ClientFunctions(net.ServerFunctions):
        from client import client_function

*Server.py*

.. code-block:: python

    class ServerFunctions(net.ServerFunctions):
        from server import dummy_function

    class ClientFunctions(net.ServerFunctions):
        @staticmethod
        def client_function(): ...

Which version to choose?
---------------------------

:ref:`Version 1 <functions-version-1>` is the preferred one because you only need to change one file, when you add/change \
a function.

:ref:`Version 2 <functions-version-2>` may be necessary when you don`t have the source code of the other side available\
, only the function names. This version might be useful for documentation all functions.

:ref:`Version 2.1 <functions-version-2.1>` is a bit less work, than :ref:`Version 2 <functions-version-2>`, because not \
every function needs to be redefined.

Classes
-------

.. autoclass:: networking.Communication_general.Functions
    :noindex:
.. autoclass:: networking.Communication_server.ClientFunctions
    :noindex:
.. autoclass:: networking.Communication_client.ServerFunctions
    :noindex:
