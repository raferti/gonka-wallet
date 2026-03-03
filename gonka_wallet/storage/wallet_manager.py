from typing import List, Optional

from .wallet_storage import WalletStorage
from ..wallet import Wallet


class WalletManager:
    """Wallet persistence. No network operations."""

    def __init__(self, storage: WalletStorage):
        self._storage = storage

    def save(self, wallet: Wallet, name: Optional[str] = None) -> str:
        return self._storage.save(wallet.to_data(), name)

    def load(self, name: str) -> Wallet:
        data = self._storage.load(name)
        return Wallet.from_data(data)

    def list(self) -> List[str]:
        return self._storage.list()
