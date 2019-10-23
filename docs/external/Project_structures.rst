Possible project structures
============================

This page will show you different ways of structuring your project, when you work with the pynetworking library.


At the beginning there are all different approaches with their advantages and disadvantages. After that there is a more
detailed explanation of every structure.

+--------------------------+-----------------------------+-------------------------------+----------------------------+
|Name                      |  Advantages                 |Disadvantages                  | Use cases                  |
+==========================+=============================+===============================+============================+
|Single file               | + Just one file required    | - Not practical in reality    | - testing                  |
|                          | + Only one process to start |                               | - learning                 |
+--------------------------+-----------------------------+-------------------------------+----------------------------+
|Client, interface, server | + Only one interface        | - At big projects much        | - Small to medium projects |
|                          |                             |   unused Code is located at   | - Disk space is no problem |
|                          |                             |   the server and client       |                            |
+--------------------------+-----------------------------+-------------------------------+----------------------------+
|2 interfaces              | + No unused source code     | - 2 interfaces to maintain    | - Big projects             |
|                          | + Server code can be hidden |                               | - Source code is not       |
|                          |   from clients              |                               |   everywhere available     |
+--------------------------+-----------------------------+-------------------------------+----------------------------+


Single file
-----------

All Code is packed in a single file. This is good for seeing fast results and testing. You only need to run one program
and not two. Because of this, it is not possible to apply it to a real world application, because the server and client are
always separated. To see a implementation of this structure have a look at the *single_file* example in the
`pynetworking_examples <https://github.com/JulianSobott/pynetworking/tree/master/pynetworking_examples>`_ package at
github.


Client, interface, server
---------------------------

Three files *Client.py*, *Server.py*, *Interface.py* at server and client.

*Client.py*: The client is started here and client-side functions are defined here.

*Interface.py*: Most of the pynetworking important setup stuff is here. For example the necessary :doc:`Functions`,
that define
which functions are available at the client and the server.

*Server.py*: The server is started here and server-side functions are defined here.

Of course you can add more files and import them to the interface. But the basic idea is important, that you split your
server and client code and have one interface file.
To see a implementation of this structure have a look at the *client_interface_server* example in the
`pynetworking_examples <https://github.com/JulianSobott/pynetworking/tree/master/pynetworking_examples>`_ package at
github.


2 interfaces
------------

Two separate interface files. One for the client-side one for the server-side.
To see a implementation of this structure have a look at the following examples: :ref:`Version 2 <functions-version-2>`
or :ref:`Version 2.1 <functions-version-2.1>`
