.. networking documentation master file, created by
   sphinx-quickstart on Tue Feb 26 18:00:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to networking's documentation!
======================================

.. toctree::
   :maxdepth: 1
   :glob:
   :caption: Contents:

   external/Getting_started
   external/Project_structures
   external/Checklist
   external/Functions


This tool abstracts network communication to a level, where the end user don`t has to care about
network communication. Server side functions can be called at the client as they were local. Functions may be called
with parameters and may return values.

Features
--------
- Directly call functions at the remote side
- Get the return values
- Don`t care about sockets

.. _Installation:

Installation
------------

The easiest way to install is to use `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: console

   pip install networking

It is also possible to clone the repository from `Github <https://github.com/JulianSobott/networking>`_ with:

.. code-block:: console

   git clone https://github.com/JulianSobott/networking.git



Contribute
----------

- Issue Tracker: github.com/JulianSobott/networking/issues
- Source Code: github.com/JulianSobott/networking


License
-------

The project is licensed under the Apache Software License.
