from dataclasses import dataclass

from bip_utils import Bip44Coins


@dataclass(frozen=True)
class ChainConfig:
    chain_id: str
    fee_denom: str
    address_prefix: str
    node_chain_rpc_url: str
    node_chain_api_url: str = ""
    coin_type: Bip44Coins = Bip44Coins.COSMOS


DEFAULT_CHAIN_CONFIG = ChainConfig(
    chain_id="gonka-mainnet",
    fee_denom="ngonka",
    address_prefix="gonka",
    node_chain_rpc_url="http://node1.gonka.ai:8000/chain-rpc",
    node_chain_api_url="http://node1.gonka.ai:8000/chain-api",
)
