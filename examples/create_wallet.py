"""Example: create a new wallet or restore an existing one."""

from gonka_wallet import Wallet, DEFAULT_CHAIN_CONFIG

# --- 1. Create a new wallet (random mnemonic) ---
wallet = Wallet.create_new()

print("=== New wallet ===")
print(f"Address:     {wallet.address}")
print(f"Public key:  {wallet.public_key}")
print(f"Private key: {wallet.private_key}")
print(f"Mnemonic:    {wallet.mnemonic}")

# --- 2. Restore wallet from mnemonic ---
mnemonic = wallet.mnemonic  # use the mnemonic from above
restored = Wallet.from_mnemonic(mnemonic)

print("\n=== Restored from mnemonic ===")
print(f"Address:     {restored.address}")
assert restored.address == wallet.address, "Addresses must match!"
print("Addresses match ✓")

# --- 3. Restore wallet from private key ---
restored_from_key = Wallet.from_private_key(wallet.private_key)

print("\n=== Restored from private key ===")
print(f"Address:     {restored_from_key.address}")
assert restored_from_key.address == wallet.address, "Addresses must match!"
print("Addresses match ✓")

# --- 4. Custom chain config ---
from gonka_wallet import ChainConfig

custom_config = ChainConfig(
    chain_id="gonka-mainnet",
    fee_denom="ngonka",
    address_prefix="gonka",
    node_chain_rpc_url="http://node3.gonka.ai:8000/chain-rpc", # replace node2 to node3
    node_chain_api_url="http://node3.gonka.ai:8000/chain-api", # replace node2 to node3
)

wallet_custom = Wallet.create_new(config=custom_config)
print("\n=== Custom chain wallet ===")
print(f"Address:     {wallet_custom.address}")
