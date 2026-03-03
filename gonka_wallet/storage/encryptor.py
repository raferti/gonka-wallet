from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

from .base import IEncryptor

PBKDF2_ITERATIONS = 100_000
SALT_SIZE = 16
NONCE_SIZE = 16
KEY_SIZE = 32  # AES-256
TAG_SIZE = 16


class AesGcmEncryptor(IEncryptor):
    """AES-256-GCM encryption.

    Format: salt (16) + nonce (16) + tag (16) + ciphertext
    """

    def __init__(self, password: str):
        self._password = password

    def _derive_key(self, salt: bytes) -> bytes:
        return PBKDF2(
            self._password,
            salt,
            dkLen=KEY_SIZE,
            count=PBKDF2_ITERATIONS,
            hmac_hash_module=SHA256
        )

    def encrypt(self, data: bytes) -> bytes:
        salt = get_random_bytes(SALT_SIZE)
        key = self._derive_key(salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=get_random_bytes(NONCE_SIZE))
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return salt + cipher.nonce + tag + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        salt = data[:SALT_SIZE]
        nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        tag = data[SALT_SIZE + NONCE_SIZE:SALT_SIZE + NONCE_SIZE + TAG_SIZE]
        ciphertext = data[SALT_SIZE + NONCE_SIZE + TAG_SIZE:]

        key = self._derive_key(salt)
        try:
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError as e:
            raise ValueError("Decryption failed: invalid password or corrupted data") from e
