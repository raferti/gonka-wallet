from dataclasses import dataclass
from typing import List

import betterproto

from .coin import CoinDto


@dataclass
class PbAnyDto(betterproto.Message):
    type_url: str = betterproto.string_field(1)
    value: bytes = betterproto.bytes_field(2)


@dataclass
class MsgSendDto(betterproto.Message):
    """cosmos.bank.v1beta1.MsgSend"""
    from_address: str = betterproto.string_field(1)
    to_address: str = betterproto.string_field(2)
    amount: List[CoinDto] = betterproto.message_field(3)


@dataclass
class Secp256k1PublicKeyDto(betterproto.Message):
    """cosmos.crypto.secp256k1.PubKey"""
    key: bytes = betterproto.bytes_field(1)


@dataclass
class SingleDto(betterproto.Message):
    """cosmos.tx.signing.v1beta1.SignMode"""
    mode: int = betterproto.int32_field(1)  # SIGN_MODE_DIRECT = 1


@dataclass
class ModeInfoDto(betterproto.Message):
    """cosmos.tx.v1beta1.ModeInfo"""
    single: SingleDto = betterproto.message_field(1)


@dataclass
class SignerInfoDto(betterproto.Message):
    """cosmos.tx.v1beta1.SignerInfo"""
    public_key: PbAnyDto = betterproto.message_field(1)
    mode_info: ModeInfoDto = betterproto.message_field(2)
    sequence: int = betterproto.uint64_field(3)


@dataclass
class FeeDto(betterproto.Message):
    """cosmos.tx.v1beta1.Fee"""
    amount: List[CoinDto] = betterproto.message_field(1)
    gas_limit: int = betterproto.uint64_field(2)
    payer: str = betterproto.string_field(3)
    granter: str = betterproto.string_field(4)


@dataclass
class AuthInfoDto(betterproto.Message):
    """cosmos.tx.v1beta1.AuthInfo"""
    signer_infos: List[SignerInfoDto] = betterproto.message_field(1)
    fee: FeeDto = betterproto.message_field(2)


@dataclass
class TxBodyDto(betterproto.Message):
    """cosmos.tx.v1beta1.TxBody"""
    messages: List[PbAnyDto] = betterproto.message_field(1)
    memo: str = betterproto.string_field(2)
    timeout_height: int = betterproto.uint64_field(3)


@dataclass
class SignDocDto(betterproto.Message):
    """cosmos.tx.v1beta1.SignDoc"""
    body_bytes: bytes = betterproto.bytes_field(1)
    auth_info_bytes: bytes = betterproto.bytes_field(2)
    chain_id: str = betterproto.string_field(3)
    account_number: int = betterproto.uint64_field(4)


@dataclass
class TxRawDto(betterproto.Message):
    """cosmos.tx.v1beta1.TxRaw"""
    body_bytes: bytes = betterproto.bytes_field(1)
    auth_info_bytes: bytes = betterproto.bytes_field(2)
    signatures: List[bytes] = betterproto.bytes_field(3)
