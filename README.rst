pynetworking
==============

**High level network communication**

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

When you have setup everything this is an example how easy it will
be to communicate between the server and client:

At the *server:*

.. code-block:: python

   def add(number1, number2):
      return number1 + number2

To call it at the *client:*

.. code-block:: python

   result = server.add(5, 10)
   print(result) # Output: 15
   
More simple examples: https://github.com/JulianSobott/pynetworking/tree/master/pynetworking_examples

.. _Installation:

Installation
------------

The easiest way to install is to use `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: console

   pip install pynetworking

It is also possible to clone the repository from `Github <https://github.com/JulianSobott/pynetworking>`_ with:

.. code-block:: console

   git clone https://github.com/JulianSobott/pynetworking.git

Documentation
--------------

Latest stable documentation: https://pynetworking.readthedocs.io/en/latest/

Or if you want the current documentation in a branch (e.g. dev), you can clone the repository,
open the cmd and cd to the `docs` folder. You need `sphinx  <http://www.sphinx-doc.org/en/master/>`_ installed. Then
you can type `make html` and see the local created docs.

Getting started
-----------------

There is a `getting started <https://pynetworking.readthedocs.io/en/latest/external/Getting_started.html>`_ guide at
the documentation. In this guide you will learn how to write a simple login application. This guide covers all basics, that are necessary.

If you are already familiar with this library and just need a brief recap, there is a `checklist <https://pynetworking
.readthedocs.io/en/latest/external/Checklist.html>`_ for what you need in new projects.

Contribute
----------

- Issue Tracker: https://github.com/JulianSobott/pynetworking/issues
- Source Code: https://github.com/JulianSobott/pynetworking


License
-------

The project is licensed under the Apache Software License.

