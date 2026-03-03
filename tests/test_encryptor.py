import pytest

from gonka_wallet.storage.encryptor import AesGcmEncryptor


class TestEncryptDecrypt:
    def test_round_trip(self):
        enc = AesGcmEncryptor(password="secret123")
        plaintext = b"hello world sensitive data"
        ciphertext = enc.encrypt(plaintext)
        assert enc.decrypt(ciphertext) == plaintext

    def test_wrong_password(self):
        enc1 = AesGcmEncryptor(password="correct")
        enc2 = AesGcmEncryptor(password="wrong")
        ciphertext = enc1.encrypt(b"data")
        with pytest.raises(ValueError, match="Decryption failed"):
            enc2.decrypt(ciphertext)

    def test_different_ciphertexts(self):
        enc = AesGcmEncryptor(password="secret")
        plaintext = b"same data"
        ct1 = enc.encrypt(plaintext)
        ct2 = enc.encrypt(plaintext)
        assert ct1 != ct2
