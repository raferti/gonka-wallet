"""Example: save, load and list wallets using WalletManager."""

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

import tempfile
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
