Security
====================

See the general description of the security: :doc:`../external/Security`

See the implementation of the cryptography: :doc:`cryptography`.

Methods, that are called to exchange the keys:

*Server_side:* (:doc:`communication_server`)

.. literalinclude:: ../../pynetworking/Communication_server.py
    :pyobject: exchange_keys

*Client_side:* (:doc:`communication_client`)

.. literalinclude:: ../../pynetworking/Communication_client.py
    :pyobject: exchange_keys