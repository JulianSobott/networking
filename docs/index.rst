.. pynetworking documentation master file, created by
   sphinx-quickstart on Tue Feb 26 18:00:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pynetworking's documentation!
==============================================

**High level network communication**

.. toctree::
   :maxdepth: 1
   :glob:
   :caption: Contents:

   external/Getting_started
   external/Checklist
   external/Project_structures
   external/Checklist
   external/Functions
   external/Security
   internal/index


This tool abstracts network communication to a level, where you don't have to care about
network communication. Server side functions can be called at the client as they were local. Functions may be called
with parameters and may return values.

**NOTE:** This library has currently not a stable version. You are welcome, to use this library in your project and
report issues or improvements.

Features
--------
- Directly call functions at the remote side
- Get the return values
- Don't care about sockets

Example
---------

When you have :doc:`setup everything <external/Checklist>` this is an example how easy it will
be to communicate between the server and a client:

At the *server:*

.. code-block:: python

   def add(number1, number2):
      return number1 + number2

To call it at the *client:*

.. code-block:: python

   result = server.add(5, 10)
   print(result) # Output: 15


.. _Installation:

Installation
------------

The easiest way to install is to use `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: console

   pip install pynetworking

It is also possible to clone the repository from `Github <https://github.com/JulianSobott/pynetworking>`_ with:

.. code-block:: console

   git clone https://github.com/JulianSobott/pynetworking.git

Getting started
-----------------

Checkout the :doc:`getting started <external/Getting_started>` guide. In this guide you will learn how to write a simple
login application. This guide covers all basics, that are necessary.

If you are already familiar with this library and just need a brief recap, there is a
:doc:`checklist <external/Checklist>`

Contribute
----------

- Issue Tracker: https://github.com/JulianSobott/pynetworking/issues
- Source Code: https://github.com/JulianSobott/pynetworking


License
-------

The project is licensed under the Apache Software License.
