import pytest

from gonka_wallet.storage.file_backend import FileBackend


@pytest.fixture
def backend(tmp_path):
    return FileBackend(base_path=str(tmp_path), extension=".json")


class TestSaveLoad:
    def test_round_trip(self, backend):
        backend.save("wallet1", b'{"key": "value"}')
        data = backend.load("wallet1")
        assert data == b'{"key": "value"}'

    def test_duplicate_raises(self, backend):
        backend.save("wallet1", b"data")
        with pytest.raises(FileExistsError):
            backend.save("wallet1", b"data2")

    def test_load_missing_raises(self, backend):
        with pytest.raises(FileNotFoundError):
            backend.load("nonexistent")


class TestList:
    def test_returns_names(self, backend):
        backend.save("alpha", b"1")
        backend.save("beta", b"2")
        names = backend.list()
        assert sorted(names) == ["alpha", "beta"]

    def test_empty(self, backend):
        assert backend.list() == []


class TestExists:
    def test_true(self, backend):
        backend.save("wallet1", b"data")
        assert backend.exists("wallet1") is True

    def test_false(self, backend):
        assert backend.exists("nonexistent") is False
