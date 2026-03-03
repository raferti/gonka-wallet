import json
import random
import string
from typing import List, Optional

from ..dto.wallet import WalletDataDto
from .base import IDataStorage, IEncryptor


class WalletStorage:
    """High-level wallet storage with optional encryption."""

    def __init__(
        self,
        data_storage: IDataStorage,
        encryptor: Optional[IEncryptor] = None
    ):
        self._storage = data_storage
        self._encryptor = encryptor

    def _serialize(self, wallet_data: WalletDataDto) -> bytes:
        return json.dumps(wallet_data.__dict__, indent=2).encode('utf-8')

    def _deserialize(self, data: bytes) -> WalletDataDto:
        return WalletDataDto(**json.loads(data.decode('utf-8')))

    def _generate_name(self) -> str:
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        return f"wallet_{suffix}"

    def save(self, wallet_data: WalletDataDto, name: Optional[str] = None) -> str:
        if name is None:
            name = self._generate_name()

        data = self._serialize(wallet_data)
        if self._encryptor:
            data = self._encryptor.encrypt(data)

        self._storage.save(name, data)
        return name

    def load(self, name: str) -> WalletDataDto:
        data = self._storage.load(name)
        if self._encryptor:
            data = self._encryptor.decrypt(data)
        return self._deserialize(data)

    def list(self) -> List[str]:
        return self._storage.list()

    def exists(self, name: str) -> bool:
        return self._storage.exists(name)
