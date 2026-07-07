import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(password.encode())

def encrypt_message(message: str, password: str) -> bytes:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, message.encode(), None)
    # prepend salt and nonce to ciphertext
    return salt + nonce + ct

def decrypt_message(encrypted_data: bytes, password: str) -> str:
    try:
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ct = encrypted_data[28:]
        key = derive_key(password, salt)
        aesgcm = AESGCM(key)
        message = aesgcm.decrypt(nonce, ct, None)
        return message.decode()
    except Exception as e:
        return None
