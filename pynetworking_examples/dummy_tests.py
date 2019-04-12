"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()
padding_oaep = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None
)

message1 = b"1"

ciphertext = public_key.encrypt(message1, padding_oaep)

plaintext = private_key.decrypt(ciphertext, padding_oaep)
print(len(ciphertext))


message2 = b"1" * 500

ciphertext = public_key.encrypt(message2, padding_oaep)

plaintext = private_key.decrypt(ciphertext, padding_oaep)
print(len(ciphertext))
