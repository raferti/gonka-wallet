from dataclasses import dataclass
from typing import List

from .coin import CoinDto


@dataclass
class AccountResponseDto:
    """Response from account query."""
    account_number: int
    sequence: int
    code: int = 0
    log: str = ""

    @property
    def is_success(self) -> bool:
        return self.code == 0


@dataclass
class BroadcastTxResponseDto:
    """Response from broadcast transaction."""
    tx_hash: str
    code: int
    log: str

    @property
    def is_success(self) -> bool:
        return self.code == 0


@dataclass
class BalanceResponseDto:
    """Response from balance query."""
    address: str
    balances: List[CoinDto]
    code: int = 0
    log: str = ""

    @property
    def is_success(self) -> bool:
        return self.code == 0

    @property
    def is_empty(self) -> bool:
        return not self.balances

    def __str__(self) -> str:
        if self.is_empty:
            return f"Address: {self.address}\n  (empty)"
        coins = "\n".join(f"  {coin}" for coin in self.balances)
        return f"Address: {self.address}\n{coins}"


@dataclass
class SendResponseDto:
    """Response from send transaction."""
    tx_hash: str
    from_address: str
    to_address: str
    amount: str
    code: int = 0
    log: str = ""

    @property
    def is_success(self) -> bool:
        return self.code == 0

    @classmethod
    def error(cls, from_address: str, to_address: str, amount: str, log: str, code: int = 1, tx_hash: str = "") -> "SendResponseDto":
        return cls(
            tx_hash=tx_hash,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            code=code,
            log=log,
        )
