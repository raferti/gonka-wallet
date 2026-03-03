import pytest

from gonka_wallet.storage.file_backend import FileBackend
from gonka_wallet.storage.wallet_manager import WalletManager
from gonka_wallet.storage.wallet_storage import WalletStorage
from gonka_wallet.wallet import Wallet


@pytest.fixture
def manager(tmp_path):
    backend = FileBackend(base_path=str(tmp_path))
    storage = WalletStorage(data_storage=backend)
    return WalletManager(storage=storage)


class TestSaveLoad:
    def test_round_trip(self, manager, wallet):
        manager.save(wallet, name="test_wallet")
        loaded = manager.load("test_wallet")
        assert isinstance(loaded, Wallet)
        assert loaded.address == wallet.address
        assert loaded.private_key == wallet.private_key
        assert loaded.public_key == wallet.public_key
        assert loaded.mnemonic == wallet.mnemonic


class TestList:
    def test_returns_names(self, manager, wallet):
        manager.save(wallet, name="w1")
        manager.save(wallet, name="w2")
        assert sorted(manager.list()) == ["w1", "w2"]
