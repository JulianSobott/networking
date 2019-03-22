Cryptography
==============

The networking provides a mechanism to encrypt messages, that are send. Every :class:`Communicator` has its own
:class:`Cryptographer`. The cryptographer encrypts outgoing messages and decrypts incoming messages. Only the special
data is decrypted, not the header. The header is necessary to show how long the special data is, and does not contain
any sensible data.

Problem: Currently all packet data is packed to one byte_string (header + special). We only want to encrypt the special
data. We can separate these functions. Only special is simple. Then encrypt special. Pass length of encrypted simple to
header.

Question: Should be any cryptography code in Packets?
- Only explicitly?

Places where encryption could happen:

    - send_packet()
        - in packet.pack() add the cryptographer as argument # Need to add a new argument, need to keep backward compatible?
        - add function packet.pack_encrypt()
        - add function packet.full_pack() to all packets
        - add function packet.pack_only_special()