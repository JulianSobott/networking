Getting started
================
After you :ref:`installed <Installation>` the package you can start setting up your project.
There are some parts you always need to add to your project. This tutorial will guide you through all necessary parts, \
will explain them and shows alternatives.
At the end of this tutorial you will have a login application. The focus is to introduce \
the pynetworking library and not how to write a secure login application. At the end of this site you will find the \
complete code.

STEP 1: Creating the files
--------------------------

1. Create a new python project. We will name our project 'login_example', but you can choose whatever you want.
2. Create 3 files inside this project and name them :code:`client.py`, :code:`server.py` and :code:`interface.py`.
    .. note::

        There are different ways for a project structure. For more information see :doc:`Project_structures`.
        The advantage of this approach is, that it is very straightforward what each file does, and easy to maintain.


STEP 2: Defining the core functions
-----------------------------------

In this step we will define all functions that we need for a login application. We don't really care about how we could \
integrate the pynetworking library. The login process should proceed like this:

1. The client requests a login to the server
2. The server gets all necessary data for login from the client
3. The data is checked and if it is correct the client will be logged in
4. The return value of the login method will indicate whether the login was successful or failed

We start with the client functions:

*client.py*

.. code-block:: python

    def login():
        pass


    if __name__ == '__main__':
        login()

We now need a function that can be called, so we add the :code:`request_login` function to the server.

*server.py*

.. code-block:: python

    def request_login():
        pass


We add a few functions to the client and the server that we need later on:

*client.py*

.. code-block:: python

    def get_username():
        return input("Enter username: ")


    def get_password():
        return input("Enter password: ")


*server.py*

.. code-block:: python

    def is_valid_data(username, password):
        # This function just simulates a possible database access and validation
        if len(username) > 5 and len(password) > 5:
            return True
        return False

Before we connect everything with the pynetworking library, we will show you how the relevant functions :code:`login()`
and :code:`request_login` would be implemented when everything were \
just client side and no network between. We leave out all the imports for simplicity.

.. code-block:: python

    def login():
        successfully_logged_in = request_login()
        if successfully_logged_in:
            print("Successfully logged in")
        else:
            print("Login failed")

    def request_login():
        username = get_username()
        password = get_password()
        return is_valid_data(username, password)

STEP 3: Setup the 'pynetworking' stuff
------------------------------------------

But because there is always a network between a server and a client, we need another way of calling a server-side function.
This is where the pynetworking library comes in. We now need to setup a few things in the interface. We start by importing \
the pynetworking library and overriding the :doc:`Functions`. These classes define which functions can be called \
at the server/client.

*interface.py*

.. code-block:: python

    import pynetworking as net

    class ServerFunctions(net.ServerFunctions):
        """All server functions, that can be called by the client"""
        from server import request_login

    class ClientFunctions(net.ClientFunctions):
        """All client functions, that can be called by the server"""
        from client import get_username, get_password

Take a look at the :doc:`Functions` page to see alternative ways of overriding these classes.

Now we need to override the classes that are responsible for communication. You do not need to know how the
communication classes \
work. It is only important, that you don't forget to override them and don't change the attributes.

*interface.py*

.. literalinclude:: ../../pynetworking_examples/login_example/interface.py
    :language: python
    :lines: 14-21

For easier use in the later code we also create an alias of the server functions. Add this to the
interface.py file. This way we can later call functions directly from the 'server' object.

*interface.py*

.. code-block:: python

    # Put this Before all classes
    server = None # prevents import error, when using: `from interface import server`

    class ServerFunctions(net.ServerFunctions):
        ...

    class ClientCommunicator(net.ClientCommunicator):
        ...

    # Put this after all classes
    server = ServerCommunicator.remote_functions


STEP 4: Connect everything
--------------------------

In this step we will connect everything.
We start by importing the interface to both files. We can use the ``import interface`` or ``from interface import ...``
syntax. in this example we go with the second one.

*client.py*, *server.py*

.. code-block:: python

    from interface import server

Now we call the :code:`request_login()` function inside :code:`login()`

*client.py*

.. code-block:: python
    :emphasize-lines: 2

    def login():
        successfully_logged_in = server.request_login()
        if successfully_logged_in:
            print("Successfully logged in")
        else:
            print("Login failed")

As you can see the only thing that changed in compare to the client only code, is that we prepended the server object to
the :code:`request_login()` function.


At the server things are a bit different. The problem is, that one server can be connected with multiple clients. To handle \
this, you will need the :class:`ClientManager` again. Among other things, this class has a function \
:code:`get()` which return the proper :class:`ClientCommunicator`. Note that you don't need to add any arguments to the \
call and get methods. The call will return the same object as the one previously created. The proper :class:`ClientCommunicator` \
is the one who called this function. So the new code in server is:

*server.py*

.. literalinclude:: ../../pynetworking_examples/login_example/server.py
    :language: python
    :lines: 6-9

**Tip:** If you want better code completion in your IDE you can do the following:

.. code-block:: python

    from interface import ClientCommunicator

    client: ClientCommunicator = net.ClientManager().get()
    username = client.remote_functions.get_username()
    ...

STEP 5: Connecting the server and client
----------------------------------------

Finally we need to start the server and the client, and connect the client to the server.

At the client-side you can use the :class:`ServerCommunicator`, which we created previously in *interface.py*, \
to connect to the server. We are using the localhost address, \
because we only want to simulate a server. The address and port must be changed, when you move to a external server.

*client.py*

.. code-block:: python

    if __name__ == '__main__':
        address = ("127.0.0.1", 5000)
        interface.ServerCommunicator.connect(address)

When the client is connected we can login, do more stuff and finally close the connection.

*client.py*

.. code-block:: python

    if __name__ == '__main__':
        address = ("127.0.0.1", 5000)
        interface.ServerCommunicator.connect(address)
        login()
        # Do more stuff
        interface.ServerCommunicator.close_connection()

At the server side we need something that allows new connections and stores them. For this purpose there is the :class:`ClientManager` \
class. The server ip address should be either the localhost or empty. As port you can choose any high number. The :class:`ClientManager` \
takes the address and the overwritten :class:`ClientCommunicator` class as arguments. We then start it and wait for 20 seconds. \
After 20 seconds we close and stop everything. Normally you would run the server forever.

*server.py*

.. code-block:: python

    if __name__ == '__main__':
        address = ("127.0.0.1", 5000)
        client_manager = net.ClientManager(address, interface.ClientCommunicator)
        client_manager.start()
        time.sleep(20)
        client_manager.stop_listening()
        client_manager.stop_connections()

CONCLUSION
----------
Congratulations you finished your first program that communicates over the network with help of the pynetworking library.
Now you can start your server, then start the client. At the client you are prompted in the console to enter your username \
and password. Enter any random value and see if you were successfully logged in.
Some parts of the code could look pretty complicated. The good thing is, you don't have to understand what is going on, you \
just need to know how to set everything up. (If you are really interested in the stuff behind the scenes you are welcome \
to have a look at the `Github repository <https://github.com/JulianSobott/pynetworking>`_ ). The code that you have
created \
can be pretty much copy and pasted to every new project. You only need to change the function includes in *interface.py*.

WHAT IS NEXT?
-------------
You can experiment with this example code by adding own functions. Try for example creating a function with parameters and see if it still works.
You can also try what happens when an error is risen. The cool thing is, that you can code like you are really calling these functions, \
but keep in mind everything works over a network and is transmitted over a tcp-connection. When you are finished with your experiments \
you can start your own project. When starting a new project this :doc:`checklist for new projects <Checklist>` will
help you to add everything necessary. You can also checkout other example at the
`Github repository <https://github.com/JulianSobott/pynetworking/tree/master/pynetworking_examples>`__.

FINAL CODE
----------
Your final code should look something like this:

*client.py*

.. literalinclude:: ../../pynetworking_examples/login_example/client.py
    :language: python
    :linenos:

*interface.py*

.. literalinclude:: ../../pynetworking_examples/login_example/interface.py
    :language: python
    :linenos:

*server.py*

.. literalinclude:: ../../pynetworking_examples/login_example/server.py
    :language: python
    :linenos:
