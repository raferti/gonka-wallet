import pytest

from gonka_wallet.config import ChainConfig
from gonka_wallet.wallet import Wallet

KNOWN_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon art"
)


@pytest.fixture
def known_mnemonic():
    return KNOWN_MNEMONIC


@pytest.fixture
def chain_config():
    return ChainConfig(
        chain_id="test-chain",
        fee_denom="ngonka",
        address_prefix="gonka",
        node_chain_rpc_url="http://localhost:26657",
        node_chain_api_url="http://localhost:1317",
    )


@pytest.fixture
def wallet(known_mnemonic, chain_config):
    return Wallet.from_mnemonic(known_mnemonic, config=chain_config)


@pytest.fixture
def known_private_key(wallet):
    return wallet.private_key
