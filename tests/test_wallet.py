import pytest

from gonka_wallet.config import DEFAULT_CHAIN_CONFIG, ChainConfig
from gonka_wallet.dto.wallet import WalletDataDto
from gonka_wallet.wallet import Wallet


class TestCreateNew:
    def test_creates_valid_wallet(self):
        w = Wallet.create_new()
        assert w.address.startswith(DEFAULT_CHAIN_CONFIG.address_prefix)
        assert len(w.private_key) == 64
        assert w.mnemonic
        assert w.public_key

    def test_custom_prefix(self):
        config = ChainConfig(
            chain_id="custom",
            fee_denom="stake",
            address_prefix="custom",
            node_chain_rpc_url="http://localhost:26657",
        )
        w = Wallet.create_new(config=config)
        assert w.address.startswith("custom")


class TestFromMnemonic:
    def test_deterministic(self, known_mnemonic, chain_config):
        w1 = Wallet.from_mnemonic(known_mnemonic, config=chain_config)
        w2 = Wallet.from_mnemonic(known_mnemonic, config=chain_config)
        assert w1.address == w2.address
        assert w1.private_key == w2.private_key
        assert w1.public_key == w2.public_key

    def test_invalid_mnemonic(self):
        with pytest.raises(ValueError, match="Invalid mnemonic"):
            Wallet.from_mnemonic("invalid words here")


class TestFromPrivateKey:
    def test_restore(self, wallet, known_private_key, chain_config):
        restored = Wallet.from_private_key(known_private_key, config=chain_config)
        assert restored.address == wallet.address
        assert restored.public_key == wallet.public_key
        assert restored.mnemonic == ""

    def test_strips_0x_prefix(self, wallet, known_private_key, chain_config):
        restored = Wallet.from_private_key("0x" + known_private_key, config=chain_config)
        assert restored.address == wallet.address

    def test_invalid_key(self):
        with pytest.raises(ValueError, match="Invalid private key"):
            Wallet.from_private_key("not_a_hex_key")

    def test_wrong_length(self):
        with pytest.raises(ValueError, match="Invalid private key"):
            Wallet.from_private_key("abcd")


class TestFromDataToData:
    def test_round_trip(self, wallet):
        data = wallet.to_data()
        assert isinstance(data, WalletDataDto)
        restored = Wallet.from_data(data)
        assert restored.address == wallet.address
        assert restored.private_key == wallet.private_key
        assert restored.public_key == wallet.public_key
        assert restored.mnemonic == wallet.mnemonic


class TestRepr:
    def test_contains_address(self, wallet):
        r = repr(wallet)
        assert wallet.address in r
        assert "Wallet" in r
