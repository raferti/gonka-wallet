from dataclasses import dataclass


@dataclass
class WalletDataDto:
    address: str
    public_key: str
    private_key: str
    mnemonic: str = ""
