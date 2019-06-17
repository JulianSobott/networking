Security
==========

Although the goal of this library is easy and fast usability, some security
aspects were implemented. In short: All messages are encrypted with a symmetric communication key,
that only the server and the client knows. The key exchange is asymmetric.

Procedure to provide a minimal security:
-----------------------------------------

This process is automatically executed, after a client has connected to a server.

- The client creates a public and private key pair
- The public key is sent to the server as plain text
- The server generates a symmetric communication key
- The server encrypts the communication key with the clients public key
- The encrypted communication key is sent back to the client
- The client decrypts the communication key with its private key
- Both sides store the communication key
- All messages are now encrypted with the communication key

Security vulnerabilities!
-------------------------

This procedure is not secure against
`Man in the middle attacks <https://en.wikipedia.org/wiki/Man-in-the-middle_attack>`_.
A method to prevent this will maybe be implemented in a later update. As long as this is not implemented,
do **NOT** use this library, when you want to transfer critical data.

For experts:
------------

If you want to see the implementation of this have a look at the :doc:`../internal/security` docs.
