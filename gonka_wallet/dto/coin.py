from dataclasses import dataclass

import betterproto


@dataclass
class CoinDto(betterproto.Message):
    denom: str = betterproto.string_field(1)
    amount: str = betterproto.string_field(2)

    def __str__(self) -> str:
        return f"{self.amount} {self.denom}"


class GonkaCoinDto(CoinDto):
    def __init__(self, amount: str):
        super().__init__(denom="gonka", amount=amount)


class NanoGonkaCoinDto(CoinDto):
    def __init__(self, amount: str):
        super().__init__(denom="ngonka", amount=amount)
