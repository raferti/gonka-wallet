"""Gonka wallet: offline key management and persistence."""

import base64
import hashlib
from typing import Tuple

import bech32
from Crypto.Hash import RIPEMD160
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Changes, Bip44Coins, Secp256k1PrivateKey
from mnemonic import Mnemonic

from .config import DEFAULT_CHAIN_CONFIG, ChainConfig
from .dto.wallet import WalletDataDto

class Wallet:
    """Offline wallet. No network operations."""

    def __init__(self, address: str, public_key: str, private_key: str, mnemonic: str = ""):
        self._address = address
        self._public_key = public_key
        self._private_key = private_key
        self._mnemonic = mnemonic

    @property
    def address(self) -> str:
        return self._address

    @property
    def public_key(self) -> str:
        return self._public_key

    @property
    def private_key(self) -> str:
        return self._private_key

    @property
    def mnemonic(self) -> str:
        return self._mnemonic

    @classmethod
    def create_new(cls, config: ChainConfig = DEFAULT_CHAIN_CONFIG) -> "Wallet":
        """Generate a new wallet with a random mnemonic."""
        mnemonic_str = Mnemonic("english").generate(strength=256)
        return cls.from_mnemonic(mnemonic_str, config=config)

    @classmethod
    def from_mnemonic(cls, mnemonic: str, config: ChainConfig = DEFAULT_CHAIN_CONFIG) -> "Wallet":
        """Restore wallet from mnemonic phrase."""
        if not Mnemonic("english").check(mnemonic):
            raise ValueError("Invalid mnemonic.")

        private_key_bytes, public_key_bytes = _derive_keys(mnemonic, config.coin_type)
        address = _pubkey_to_address(public_key_bytes, config.address_prefix)
        priv_hex, pub_b64 = _keys_to_str(private_key_bytes, public_key_bytes)
        return cls(address=address, public_key=pub_b64, private_key=priv_hex, mnemonic=mnemonic)

    @classmethod
    def from_private_key(cls, private_key_hex: str, config: ChainConfig = DEFAULT_CHAIN_CONFIG) -> "Wallet":
        """Restore wallet from private key hex. Mnemonic will be empty."""
        if private_key_hex.startswith("0x"):
            private_key_hex = private_key_hex[2:]

        try:
            private_key_bytes = bytes.fromhex(private_key_hex)
            if len(private_key_bytes) != 32:
                raise ValueError("Private key must be 32 bytes (64 hex characters)")
        except ValueError as e:
            raise ValueError(f"Invalid private key: {e}") from e

        priv_key_obj = Secp256k1PrivateKey.FromBytes(private_key_bytes)
        public_key_bytes = priv_key_obj.PublicKey().RawCompressed().ToBytes()

        address = _pubkey_to_address(public_key_bytes, config.address_prefix)
        priv_hex, pub_b64 = _keys_to_str(private_key_bytes, public_key_bytes)
        return cls(address=address, public_key=pub_b64, private_key=priv_hex, mnemonic="")

    @classmethod
    def from_data(cls, data: WalletDataDto) -> "Wallet":
        """Create wallet from WalletDataDto."""
        return cls(
            address=data.address,
            public_key=data.public_key,
            private_key=data.private_key,
            mnemonic=data.mnemonic,
        )

    def to_data(self) -> WalletDataDto:
        """Export wallet as WalletDataDto."""
        return WalletDataDto(
            address=self._address,
            public_key=self._public_key,
            private_key=self._private_key,
            mnemonic=self._mnemonic,
        )

    def __repr__(self) -> str:
        return f"Wallet(address={self._address!r})"



# --- Helper functions (module-private) ---

def _derive_keys(mnemonic: str, coin_type: Bip44Coins = Bip44Coins.COSMOS) -> Tuple[bytes, bytes]:
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_ctx = (
        Bip44.FromSeed(seed, coin_type)
        .Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )
    private_key = bip44_ctx.PrivateKey().Raw().ToBytes()
    public_key = bip44_ctx.PublicKey().RawCompressed().ToBytes()
    return private_key, public_key


def _pubkey_to_address(public_key: bytes, prefix: str) -> str:
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160_hash = RIPEMD160.new(sha256_hash).digest()
    five_bit_data = bech32.convertbits(ripemd160_hash, 8, 5, True)
    return bech32.bech32_encode(prefix, five_bit_data)


def _keys_to_str(private_key: bytes, public_key: bytes) -> Tuple[str, str]:
    return private_key.hex(), base64.b64encode(public_key).decode()
