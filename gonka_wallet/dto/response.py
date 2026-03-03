from dataclasses import dataclass
from typing import List

from .coin import CoinDto


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


@dataclass
class SendResponseDto:
    """Response from send transaction."""
    tx_hash: str
    from_address: str
    to_address: str
    amount: int
    code: int = 0
    log: str = ""

    @property
    def is_success(self) -> bool:
        return self.code == 0

    @classmethod
    def error(cls, from_address: str, to_address: str, amount: int, code: int, log: str) -> "SendResponseDto":
        return cls(
            tx_hash="",
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            code=code,
            log=log
        )
