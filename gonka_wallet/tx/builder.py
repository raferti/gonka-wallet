import hashlib
from typing import List

from ecdsa import SECP256k1, SigningKey
from ecdsa.util import sigencode_string_canonize

from ..dto.coin import CoinDto
from ..dto.transaction import (
    AuthInfoDto,
    FeeDto,
    ModeInfoDto,
    MsgSendDto,
    PbAnyDto,
    Secp256k1PublicKeyDto,
    SignDocDto,
    SignerInfoDto,
    SingleDto,
    TxBodyDto,
    TxRawDto,
)


MSG_SEND_TYPE_URL = "/cosmos.bank.v1beta1.MsgSend"
PUBKEY_TYPE_URL = "/cosmos.crypto.secp256k1.PubKey"
SIGN_MODE_DIRECT = 1


class TxBuilder:
    """Build and sign Cosmos SDK transactions."""

    def __init__(self, chain_id: str):
        self.chain_id = chain_id

    def build_send_tx(
        self,
        private_key_hex: str,
        from_address: str,
        to_address: str,
        amount: CoinDto,
        account_number: int,
        sequence: int,
        gas_limit: int = 200_000,
        fee_amount: int = 0,
        fee_denom: str = "",
        memo: str = "",
    ) -> bytes:
        """Build and sign a MsgSend transaction."""
        msg_send = MsgSendDto(
            from_address=from_address,
            to_address=to_address,
            amount=[amount],
        )
        msg_any = PbAnyDto(
            type_url=MSG_SEND_TYPE_URL,
            value=bytes(msg_send),
        )

        return self._build_and_sign(
            messages=[msg_any],
            private_key_hex=private_key_hex,
            account_number=account_number,
            sequence=sequence,
            gas_limit=gas_limit,
            fee_amount=fee_amount,
            fee_denom=fee_denom or amount.denom,
            memo=memo,
        )

    def _build_and_sign(
        self,
        messages: List[PbAnyDto],
        private_key_hex: str,
        account_number: int,
        sequence: int,
        gas_limit: int,
        fee_amount: int,
        fee_denom: str,
        memo: str = "",
    ) -> bytes:
        """Build, sign and serialize a transaction with arbitrary messages."""
        private_key_bytes = bytes.fromhex(private_key_hex)
        signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        public_key_bytes = signing_key.get_verifying_key().to_string("compressed")

        body_bytes = bytes(TxBodyDto(
            messages=messages,
            memo=memo,
            timeout_height=0,
        ))

        auth_info_bytes = bytes(self._build_auth_info(
            public_key_bytes, sequence, gas_limit, fee_amount, fee_denom,
        ))

        sign_doc_bytes = bytes(SignDocDto(
            body_bytes=body_bytes,
            auth_info_bytes=auth_info_bytes,
            chain_id=self.chain_id,
            account_number=account_number,
        ))

        signature = self._sign(sign_doc_bytes, signing_key)

        return bytes(TxRawDto(
            body_bytes=body_bytes,
            auth_info_bytes=auth_info_bytes,
            signatures=[signature],
        ))

    def _build_auth_info(
        self, public_key_bytes: bytes, sequence: int,
        gas_limit: int, fee_amount: int, fee_denom: str,
    ) -> AuthInfoDto:
        """Build AuthInfo with public key and fee."""
        pub_key_any = PbAnyDto(
            type_url=PUBKEY_TYPE_URL,
            value=bytes(Secp256k1PublicKeyDto(key=public_key_bytes)),
        )

        signer_info = SignerInfoDto(
            public_key=pub_key_any,
            mode_info=ModeInfoDto(single=SingleDto(mode=SIGN_MODE_DIRECT)),
            sequence=sequence,
        )

        fee = FeeDto(
            amount=[CoinDto(denom=fee_denom, amount=str(fee_amount))],
            gas_limit=gas_limit,
            payer="",
            granter="",
        )

        return AuthInfoDto(signer_infos=[signer_info], fee=fee)

    @staticmethod
    def _sign(sign_doc_bytes: bytes, signing_key: SigningKey) -> bytes:
        """Sign the SignDoc bytes with ECDSA secp256k1."""
        message_hash = hashlib.sha256(sign_doc_bytes).digest()
        return signing_key.sign_digest(
            message_hash,
            sigencode=sigencode_string_canonize,
        )
