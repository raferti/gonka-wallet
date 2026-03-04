# gonka-wallet

Wallet library for the Gonka chain. Offline key management, transaction building, and network queries.

## Installation

```bash
pip install gonka-wallet
```

## Features

- **Offline wallet** — create, restore from mnemonic or private key
- **Transaction builder** — build and sign transactions
- **Network client** — balance queries, transaction broadcasting, vesting queries
- **Encrypted storage** — AES-256-GCM wallet encryption with password
- **No external key servers** — all cryptography runs locally
- **Wallet manager** — save, load, and list wallets with optional AES-256-GCM encryption

## Quick Start

### Wallet
Examples of creating a wallet object in different ways.

```python
from gonka_wallet import Wallet

# Create a new wallet (offline, no network)
wallet = Wallet.create_new()
print(
    f"Address: {wallet.address} "
    f"Mnemonic: {wallet.mnemonic} "
    f"Public key: {wallet.public_key} "
    f"Private key: {wallet.private_key}"
)


# Restore from mnemonic (offline, no network)
wallet = Wallet.from_mnemonic("your 24 word mnemonic phrase ...")
print(
    f"Address: {wallet.address} "
    f"Mnemonic: {wallet.mnemonic} "
    f"Public key: {wallet.public_key} "
    f"Private key: {wallet.private_key}"
)


# Wallet object from private key (offline, no network)
wallet = Wallet.from_private_key("your private key ...")
print(
    f"Address: {wallet.address} "
    f"Public key: {wallet.public_key} "
    f"Private key: {wallet.private_key}"
)
```

### Token management

Balance query example:
```python
from gonka_wallet import GonkaClient, DEFAULT_CHAIN_CONFIG

GONKA_ADDRESS = "gonka1..." # your gonka wallet address

with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    try:
        response = client.balance(GONKA_ADDRESS)
    # Handle standard network errors
    except Exception as e:
        print(e)

# Checking the response from the blockchain
if response.is_success:
    if response.balances:
        print(f"Address: {response.address} ")
        for coin in response.balances:
            print(f"{coin.amount} {coin.denom}")
    else:
        print(f"Balance is empty")
else:
    print(f"Query failed (code={response.code}): {response.log}")
```

Vesting balance query example:
```python
from gonka_wallet import GonkaClient, DEFAULT_CHAIN_CONFIG

GONKA_ADDRESS = "gonka1..." # your gonka wallet address

# Query vesting balance
with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    try:
        response = client.vesting_balance(GONKA_ADDRESS)
    # Handle standard network errors
    except Exception as e:
        print(e)

# Checking the response from the blockchain
if response.is_success:
    if response.balances:
        print(f"Address: {response.address} ")
        for coin in response.balances:
            print(f"{coin.amount} {coin.denom}")
    else:
        print(f"Balance is empty")
else:
    print(f"Query failed (code={response.code}): {response.log}")
```

Token transfer example:
```python
from gonka_wallet import GonkaClient, DEFAULT_CHAIN_CONFIG, gonka_to_ngonka
from gonka_wallet.dto.coin import GonkaCoinDto, NanoGonkaCoinDto

# Replace these values before running
PRIVATE_KEY  = "your_private_key_hex_here"
FROM_ADDRESS = "gonka1..."
TO_ADDRESS   = "gonka1..."

# Amount to send
AMOUNT_GONKA = 1.0  # in GONKA

amount = GonkaCoinDto(amount=str(AMOUNT_GONKA))
# You can specify the value in ngonka
# amount = NanoGonkaCoinDto(amount="100")
# or convert the value in gonka to ngonka using the function "gonka_to_ngonka"
# amount = NanoGonkaCoinDto(amount=str(gonka_to_ngonka(AMOUNT_GONKA)))

# Example 1:
# Node checks the tx before responding — is_success reflects the actual result.
with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    response = client.send(
        private_key=PRIVATE_KEY,
        from_address=FROM_ADDRESS,
        to_address=TO_ADDRESS,
        amount=amount,
        gas_limit=200_000,
        fee_amount=0,
        memo="sent via python gonka_wallet",
    )

if response.is_success:
    print(f"Transaction sent!")
    print(f"  TX hash:  {response.tx_hash}")
    print(f"  From:     {response.from_address}")
    print(f"  To:       {response.to_address}")
    print(f"  Amount:   {response.amount} ngonka ({AMOUNT_GONKA} GONKA)")
else:
    print(f"Transaction failed (code={response.code}): {response.log}")
    if response.tx_hash:
        print(f"  TX hash: {response.tx_hash}")
    else:
        print("  TX was not accepted by the chain")
```

### Configuration
The default parameters required for wallet creation, balance queries, and token transfers
are stored in `DEFAULT_CHAIN_CONFIG` and defined using the `ChainConfig` dataclass:
```python
from gonka_wallet.config import ChainConfig

DEFAULT_CHAIN_CONFIG = ChainConfig(
    chain_id="gonka-mainnet",
    fee_denom="ngonka",
    address_prefix="gonka",
    node_chain_rpc_url="http://node1.gonka.ai:8000/chain-rpc",
    node_chain_api_url="http://node1.gonka.ai:8000/chain-api",
)
```
You can create a custom config — for example, overriding the genesis node URLs used for blockchain requests — and pass it to the client. All requests will then go through the nodes you specified.
```python
from gonka_wallet import GonkaClient
from gonka_wallet.config import ChainConfig

CUSTOM_CHAIN_CONFIG = ChainConfig(
    chain_id="gonka-mainnet",
    fee_denom="ngonka",
    address_prefix="gonka",
    # replace http://node1... to http://node3...
    node_chain_rpc_url="http://node3.gonka.ai:8000/chain-rpc",
    node_chain_api_url="http://node3.gonka.ai:8000/chain-api",
)

with GonkaClient(CUSTOM_CHAIN_CONFIG) as client:
    response = client.send(...)
```
*The list of available genesis nodes can be found on the project page at [gonka.ai](https://gonka.ai/developer/quickstart/#1-define-variables)*

### Wallet management

`WalletManager` lets you save wallet data either encrypted or in plain text, list previously saved wallets, and load (reconstruct) a wallet object from a saved entry.

Encrypted storage currently uses the AES-256-GCM algorithm. If this method doesn't suit your needs, you can implement your own encryptor class and pass it to `WalletManager`.

For saving, loading, and listing wallets, `WalletManager` uses `FileBackend` by default — meaning all operations work with files on disk. You can easily switch to a different storage backend (e.g. a database) by implementing and passing the appropriate class to `WalletManager`.

Wallet manager usage example:
```python
import tempfile

from gonka_wallet import Wallet
from gonka_wallet.storage.file_backend import FileBackend
from gonka_wallet.storage.wallet_storage import WalletStorage
from gonka_wallet.storage.wallet_manager import WalletManager
from gonka_wallet.storage.encryptor import AesGcmEncryptor

# Use a temp directory so the example is self-contained and leaves no files behind.
# Replace with a real path, e.g. "./my_wallets", to persist wallets on disk.
wallet_dir = tempfile.mkdtemp(prefix="gonka_wallets_")
print(f"Wallet directory: {wallet_dir}\n")


# ── 1. Plain storage (no encryption) ────────────────────────────────────────

backend = FileBackend(base_path=wallet_dir, extension=".json")
storage = WalletStorage(data_storage=backend)
manager = WalletManager(storage=storage)

# Create and save two wallets
alice = Wallet.create_new()
bob   = Wallet.create_new()

manager.save(alice, name="alice")
manager.save(bob,   name="bob")

print("=== Saved wallets ===")
print(f"  alice → {alice.address}")
print(f"  bob   → {bob.address}")

# List all wallets
names = manager.list()
print(f"\n=== All wallets ({len(names)}) ===")
for name in names:
    print(f"  {name}")

# Load wallet by name
loaded_alice = manager.load("alice")
print(f"\n=== Loaded 'alice' ===")
print(f"  Address:    {loaded_alice.address}")
print(f"  Public key: {loaded_alice.public_key}")
assert loaded_alice.address == alice.address, "Addresses must match!"
print("  Addresses match ✓")


# ── 2. Encrypted storage (AES-256-GCM) ──────────────────────────────────────

enc_dir = tempfile.mkdtemp(prefix="gonka_wallets_enc_")
print(f"\nEncrypted wallet directory: {enc_dir}\n")

PASSWORD = "super_secret_password"

enc_backend  = FileBackend(base_path=enc_dir, extension=".enc")
encryptor    = AesGcmEncryptor(password=PASSWORD)
enc_storage  = WalletStorage(data_storage=enc_backend, encryptor=encryptor)
enc_manager  = WalletManager(storage=enc_storage)

# Save wallet with auto-generated name
carol = Wallet.create_new()
auto_name = enc_manager.save(carol)          # name is generated automatically

print("=== Saved encrypted wallet ===")
print(f"  Auto name: {auto_name}")
print(f"  Address:   {carol.address}")

# Load it back — must use the same password
loaded_carol = enc_manager.load(auto_name)
print(f"\n=== Loaded encrypted wallet ===")
print(f"  Address: {loaded_carol.address}")
assert loaded_carol.address == carol.address, "Addresses must match!"
print("  Addresses match ✓")

# Wrong password → raises ValueError
wrong_manager = WalletManager(
    storage=WalletStorage(
        data_storage=enc_backend,
        encryptor=AesGcmEncryptor(password="wrong_password"),
    )
)
try:
    wrong_manager.load(auto_name)
except ValueError as e:
    print(f"\n  Wrong password raises ValueError: {e}")
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
