import pytest
from dataclasses import FrozenInstanceError

from gonka_wallet.config import ChainConfig, DEFAULT_CHAIN_CONFIG


class TestChainConfig:
    def test_required_fields(self, chain_config):
        assert chain_config.chain_id == "test-chain"
        assert chain_config.fee_denom == "ngonka"
        assert chain_config.address_prefix == "gonka"
        assert chain_config.node_chain_rpc_url == "http://localhost:26657"

    def test_default_config_values(self):
        assert DEFAULT_CHAIN_CONFIG.chain_id == "gonka-mainnet"
        assert DEFAULT_CHAIN_CONFIG.fee_denom == "ngonka"
        assert DEFAULT_CHAIN_CONFIG.address_prefix == "gonka"
        assert DEFAULT_CHAIN_CONFIG.node_chain_rpc_url == "http://node2.gonka.ai:8000/chain-rpc"
        assert DEFAULT_CHAIN_CONFIG.node_chain_api_url == "http://node2.gonka.ai:8000/chain-api"

    def test_frozen(self):
        with pytest.raises(FrozenInstanceError):
            DEFAULT_CHAIN_CONFIG.chain_id = "other"
