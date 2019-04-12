from OpenSSL import crypto


ENCODING = "utf-8"


def create_key_pair(key_type, bits) -> crypto.PKey:
    pkey = crypto.PKey()
    pkey.generate_key(key_type, bits)
    return pkey


def create_cert_request(pkey, digest="sha256", **name) -> crypto.X509Req:
    """
       Create a certificate request.
       Arguments: pkey   - The key to associate with the request
                  digest - Digestion method to use for signing, default is sha256
                  **name - The name of the subject of the request, possible
                           arguments are:
                             C     - Country name
                             ST    - State or province name
                             L     - Locality name
                             O     - Organization name
                             OU    - Organizational unit name
                             CN    - Common name
                             emailAddress - E-mail address
       """
    req = crypto.X509Req()
    subj = req.get_subject()

    for key, value in name.items():
        setattr(subj, key, value)

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req


def create_certificate(req, issuer_cert_key, serial, validity_period, digest="sha256") -> crypto.X509:
    """
        Generate a certificate given a certificate request.
        Arguments: req        - Certificate request to use
                   issuerCert - The certificate of the issuer
                   issuerKey  - The private key of the issuer
                   serial     - Serial number for the certificate
                   notBefore  - Timestamp (relative to now) when the certificate
                                starts being valid
                   notAfter   - Timestamp (relative to now) when the certificate
                                stops being valid
                   digest     - Digest method to use for signing, default is sha256
        Returns:   The signed certificate in an X509 object
        """
    issuer_cert, issuer_key = issuer_cert_key
    not_before, not_after = validity_period
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(not_before)
    cert.gmtime_adj_notAfter(not_after)
    cert.set_issuer(issuer_cert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(issuer_key, digest)
    return cert
