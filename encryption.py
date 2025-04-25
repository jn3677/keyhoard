import os
import base64
import json

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from test import cipher

backend = default_backend()

def generate_salt():
    return os.urandom(16)

def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )
    return kdf.derive(password.encode())

def encrypt(plaintext: str, key: bytes):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    # Pad plain text to 16-byte block
    padding = 16 - len(plaintext.encode()) % 16
    padded = plaintext + chr(padding) * padding
    ct = encryptor.update(padded.encode()) + encryptor.finalize()

    return base64.b64encode(iv + ct).decode()


def decrypt(ciphertext_b64: str, key: bytes):
    raw = base64.b64decode(ciphertext_b64)
    iv = raw[:16]
    ct = raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()

    padding = padded[-1]

    if padding < 1 or padding > 16:
        raise ValueError("Invalid padding length.")

    # Validate padding bytes are all the same
    if padded[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding bytes.")
    return padded[:-padding].decode()