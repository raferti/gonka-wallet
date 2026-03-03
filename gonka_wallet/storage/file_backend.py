import os
from typing import List

from .base import IDataStorage


class FileBackend(IDataStorage):
    """File-based storage for raw bytes."""

    def __init__(self, base_path: str, extension: str = ".json"):
        self._base_path = base_path
        self._extension = extension
        os.makedirs(self._base_path, exist_ok=True)

    def _get_path(self, identifier: str) -> str:
        return os.path.join(self._base_path, f"{identifier}{self._extension}")

    def save(self, identifier: str, data: bytes) -> None:
        path = self._get_path(identifier)
        if os.path.exists(path):
            raise FileExistsError(f"File already exists: {path}")
        with open(path, "wb") as f:
            f.write(data)

    def load(self, identifier: str) -> bytes:
        path = self._get_path(identifier)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "rb") as f:
            return f.read()

    def list(self) -> List[str]:
        if not os.path.exists(self._base_path):
            return []
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(self._base_path)
            if f.endswith(self._extension) and
               os.path.isfile(os.path.join(self._base_path, f))
        ]

    def exists(self, identifier: str) -> bool:
        return os.path.exists(self._get_path(identifier))
