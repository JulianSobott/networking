import os
from OpenSSL import crypto

from cert_gen import create_key_pair, create_cert_request, create_certificate


ENCODING = "utf-8"
certificate_folder = "certificates/"

cakey = create_key_pair(crypto.TYPE_RSA, 2048)
careq = create_cert_request(cakey, CN='Certificate Authority')
# CA certificate is valid for five years
cacert = create_certificate(careq, (careq, cakey), 0, (0, 60*60*24*365*5))

print("Creating Certificate Authority private key in 'CA.pkey'")
with open(os.path.join(certificate_folder, "CA.pkey"), "w") as capkey:
    capkey.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, cakey).decode(ENCODING))

print('Creating Certificate Authority certificate in "CA.cert"')
with open(os.path.join(certificate_folder, "CA.cert"), "w") as ca:
    ca.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cacert).decode(ENCODING))

for fname, cname in [("client", "Client"), ("server", "Server")]:
    pkey = create_key_pair(crypto.TYPE_RSA, 2048)
    req = create_cert_request(pkey, CN=cname)
    # Certificates are valid for five years.
    cert = create_certificate(req, (cacert, cakey), 1, (0, 60 * 60 * 24 * 365 * 5))

    print(f"Creating Certificate {fname} private key in {fname}.pkey")
    with open(os.path.join(certificate_folder, f"{fname}.pkey"), 'w') as leafpkey:
        leafpkey.write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey).decode(ENCODING)
        )

    print(f"Creating Certificate {fname} certificate in f{fname}.cert")
    with open(os.path.join(certificate_folder, f"{fname}.cert"), 'w') as leafcert:
        leafcert.write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode(ENCODING)
        )
