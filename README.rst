High level network communication

This tool abstracts network communication to a level, where the end user don`t has to care about
network communication. Server side functions can be called at the client as they were local. Functions may be called
with parameters and may return values.

**NOTE:** This library is in development process. There may be big changes to it.

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

   pip install pynetworking

It is also possible to clone the repository from `Github <https://github.com/JulianSobott/networking>`_ with:

.. code-block:: console

   git clone https://github.com/JulianSobott/networking.git

Documentation
--------------

To view latest stable documentation goto: https://networking.readthedocs.io/en/latest/

Or if you want the current documentation in a branch (e.g. dev), you can clone the repository,
open the cmd and cd to the `docs` folder. You need `sphinx  <http://www.sphinx-doc.org/en/master/>`_ installed. Then
you can type `make html` and see the local created docs.

Contribute
----------

- Issue Tracker: github.com/JulianSobott/networking/issues
- Source Code: github.com/JulianSobott/networking


License
-------

The project is licensed under the Apache Software License.

