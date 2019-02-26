# -*- coding: latin-1 -*-
#
# Copyright (C) AB Strakt
# Copyright (C) Jean-Paul Calderone
# See LICENSE for details.

"""
Simple echo server, using nonblocking I/O
"""
import os
import select
import socket
import sys

from OpenSSL import SSL, crypto

ENCODING = "utf-8"
PORT = 5000
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
ctx.set_verify(
    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb
)  # Demand a certificate
ctx.use_privatekey_file(os.path.join(certificate_folder, 'server.pkey'))
ctx.use_certificate_file(os.path.join(certificate_folder, 'server.cert'))
ctx.load_verify_locations(os.path.join(certificate_folder, 'CA.cert'))

# Set up server
server = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
server.bind(('', PORT))
server.listen(3)
server.setblocking(0)

clients = {}
writers = {}


def dropClient(cli, errors=None):
    if errors:
        print('Client %s left unexpectedly:' % (clients[cli],))
        print('  ', errors)
    else:
        print('Client %s left politely' % (clients[cli],))
    del clients[cli]
    if cli in writers:
        del writers[cli]
    if not errors:
        cli.shutdown()
    cli.close()


while True:
    try:
        r, w, _ = select.select(
            [server] + list(clients.keys()), list(writers.keys()), []
        )
    except Exception:
        break

    for cli in r:
        if cli == server:
            cli, addr = server.accept()
            print('Connection from %s' % (addr,))
            clients[cli] = addr

        else:
            try:
                ret = cli.recv(1024).decode(ENCODING)
            except (SSL.WantReadError,
                    SSL.WantWriteError,
                    SSL.WantX509LookupError):
                pass
            except SSL.ZeroReturnError:
                dropClient(cli)
            except SSL.Error as errors:
                dropClient(cli, errors)
            else:
                if cli not in writers:
                    writers[cli] = ''
                writers[cli] = writers[cli] + ret

    for cli in w:
        try:
            ret = cli.send(bytes(writers[cli], ENCODING))
        except (SSL.WantReadError,
                SSL.WantWriteError,
                SSL.WantX509LookupError):
            pass
        except SSL.ZeroReturnError:
            dropClient(cli)
        except SSL.Error as errors:
            dropClient(cli, errors)
        else:
            writers[cli] = writers[cli][ret:]
            if writers[cli] == '':
                del writers[cli]

for cli in clients.keys():
    cli.close()
server.close()
