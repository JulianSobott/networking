# -*- coding: latin-1 -*-
#
# Copyright (C) AB Strakt
# Copyright (C) Jean-Paul Calderone
# See LICENSE for details.

"""
Simple SSL client, using blocking I/O
"""

import os
import socket
import sys

from OpenSSL import SSL, crypto


ADDRESS, PORT = "127.0.0.1", 5000
certificate_folder = "certificates/"


def verify_cb(conn, cert, errnum, depth, ok):
    certsubject = crypto.X509Name(cert.get_subject())
    commonname = certsubject.commonName
    print('Got certificate: ' + commonname)
    return ok


# Initialize context
ctx = SSL.Context(SSL.SSLv23_METHOD)
ctx.set_options(SSL.OP_NO_SSLv2)
ctx.set_options(SSL.OP_NO_SSLv3)
ctx.set_verify(SSL.VERIFY_PEER, verify_cb)  # Demand a certificate
ctx.use_privatekey_file(os.path.join(certificate_folder, 'client.pkey'))
ctx.use_certificate_file(os.path.join(certificate_folder, 'client.cert'))
ctx.load_verify_locations(os.path.join(certificate_folder, 'CA.cert'))

# Set up client
sock = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
sock.connect((ADDRESS, PORT))

while True:
    line = sys.stdin.readline()
    if line == '':
        break
    try:
        sock.send(bytes(line, 'utf-8'))
        sys.stdout.write(sock.recv(1024).decode('utf-8'))
        sys.stdout.flush()
    except SSL.Error:
        print('Connection died unexpectedly')
        break


sock.shutdown()
sock.close()
