Next steps
==============


File receiving
-----------------

It is possible to send a file from client to server and server to client. The file data is exactly the
same. Met data may be changed. Possible to keep meta data? Possible between different os? The file is sent in chunks.
This will avoid huge memory usage. Every chunk is read sent and deleted. Then immaterially written
into the new file. As soon as a MetaFilePacket is received, the normal chunk receive process is paused
and all new data is written to the file. The receive stuff is inside the open contextmanager to avoid
rapid opening and closing of the file. Receive must also handle errors like general receive. Extract general stuff
into function. Then have two functions. One receive packets the other receive files. What happens when the
file is fully received and new Packet data arrives. Must be sent to the Packet receiver function.
Important define how much bytes the socket should recv inside a loop. All other data is stored in a buffer
and is translated to the packet function, when the file function finishes.