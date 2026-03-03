# gonka-wallet

Wallet library for the Gonka chain. Offline key management, transaction building, and network queries.

## Installation

```bash
pip install gonka-wallet
```

## Quick Start

```python
from gonka_wallet import Wallet, GonkaClient, DEFAULT_CHAIN_CONFIG

# Create a new wallet (offline, no network)
wallet = Wallet.create_new()
print(wallet.address)
print(wallet.mnemonic)

# Restore from mnemonic
wallet = Wallet.from_mnemonic("your 24 word mnemonic phrase ...")

# Query balance
with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    balance = client.balance(wallet.address)
    print(balance.balances)
```

## Features

- **Offline wallet** — create, restore from mnemonic or private key
- **Transaction builder** — build and sign Cosmos SDK transactions
- **Network client** — balance queries, transaction broadcasting, vesting queries
- **Encrypted storage** — AES-256-GCM wallet encryption with password
- **No external key servers** — all cryptography runs locally

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
