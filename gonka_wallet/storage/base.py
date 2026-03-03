from abc import ABC, abstractmethod
from typing import List


class IDataStorage(ABC):
    """Low-level storage interface for raw bytes."""

    @abstractmethod
    def save(self, identifier: str, data: bytes) -> None:
        ...

    @abstractmethod
    def load(self, identifier: str) -> bytes:
        ...

    @abstractmethod
    def list(self) -> List[str]:
        ...

    @abstractmethod
    def exists(self, identifier: str) -> bool:
        ...


class IEncryptor(ABC):
    """Interface for encryption/decryption."""

    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        ...

    @abstractmethod
    def decrypt(self, data: bytes) -> bytes:
        ...
