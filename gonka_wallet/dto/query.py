from dataclasses import dataclass
from typing import List

import betterproto

from .coin import CoinDto
from .transaction import PbAnyDto


@dataclass
class BaseAccountDto(betterproto.Message):
    address: str = betterproto.string_field(1)
    pub_key: PbAnyDto = betterproto.message_field(2)
    account_number: int = betterproto.uint64_field(3)
    sequence: int = betterproto.uint64_field(4)


@dataclass
class QueryAllBalancesRequestDto(betterproto.Message):
    address: str = betterproto.string_field(1)


@dataclass
class QueryAllBalancesResponseDto(betterproto.Message):
    balances: List[CoinDto] = betterproto.message_field(1)


@dataclass
class QueryAccountRequestDto(betterproto.Message):
    address: str = betterproto.string_field(1)


@dataclass
class QueryAccountResponseDto(betterproto.Message):
    account: PbAnyDto = betterproto.message_field(1)
