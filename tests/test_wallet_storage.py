import pytest

from gonka_wallet.dto.wallet import WalletDataDto
from gonka_wallet.storage.encryptor import AesGcmEncryptor
from gonka_wallet.storage.file_backend import FileBackend
from gonka_wallet.storage.wallet_storage import WalletStorage


@pytest.fixture
def wallet_data():
    return WalletDataDto(
        address="gonka1test",
        public_key="pubkey_base64",
        private_key="aa" * 32,
        mnemonic="test mnemonic words",
    )


@pytest.fixture
def storage(tmp_path):
    backend = FileBackend(base_path=str(tmp_path))
    return WalletStorage(data_storage=backend)


@pytest.fixture
def encrypted_storage(tmp_path):
    backend = FileBackend(base_path=str(tmp_path), extension=".enc")
    encryptor = AesGcmEncryptor(password="test_password")
    return WalletStorage(data_storage=backend, encryptor=encryptor)


class TestSaveLoadPlain:
    def test_round_trip(self, storage, wallet_data):
        storage.save(wallet_data, name="mywallet")
        loaded = storage.load("mywallet")
        assert loaded.address == wallet_data.address
        assert loaded.private_key == wallet_data.private_key
        assert loaded.public_key == wallet_data.public_key
        assert loaded.mnemonic == wallet_data.mnemonic


class TestSaveLoadEncrypted:
    def test_round_trip(self, encrypted_storage, wallet_data):
        encrypted_storage.save(wallet_data, name="enc_wallet")
        loaded = encrypted_storage.load("enc_wallet")
        assert loaded.address == wallet_data.address
        assert loaded.private_key == wallet_data.private_key


class TestGenerateName:
    def test_auto_name(self, storage, wallet_data):
        name = storage.save(wallet_data)
        assert name.startswith("wallet_")
        assert len(name) > len("wallet_")


class TestListExists:
    def test_list(self, storage, wallet_data):
        storage.save(wallet_data, name="w1")
        storage.save(wallet_data, name="w2")
        assert sorted(storage.list()) == ["w1", "w2"]

    def test_exists(self, storage, wallet_data):
        storage.save(wallet_data, name="w1")
        assert storage.exists("w1") is True
        assert storage.exists("w2") is False
