from gonka_wallet.dto.coin import CoinDto, NanoGonkaCoinDto
from gonka_wallet.dto.transaction import TxRawDto, AuthInfoDto
from gonka_wallet.tx.builder import TxBuilder


PRIVATE_KEY_HEX = "a" * 64  # 32 bytes of 0xAA


class TestBuildSendTx:
    def test_returns_bytes(self):
        builder = TxBuilder(chain_id="test-chain")
        result = builder.build_send_tx(
            private_key_hex=PRIVATE_KEY_HEX,
            from_address="gonka1sender",
            to_address="gonka1receiver",
            amount=NanoGonkaCoinDto("1000"),
            account_number=0,
            sequence=0,
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_deserializes_to_tx_raw(self):
        builder = TxBuilder(chain_id="test-chain")
        result = builder.build_send_tx(
            private_key_hex=PRIVATE_KEY_HEX,
            from_address="gonka1sender",
            to_address="gonka1receiver",
            amount=NanoGonkaCoinDto("1000"),
            account_number=5,
            sequence=3,
        )
        tx_raw = TxRawDto().parse(result)
        assert tx_raw.body_bytes
        assert tx_raw.auth_info_bytes
        assert len(tx_raw.signatures) > 0

    def test_fee_denom_in_auth_info(self):
        builder = TxBuilder(chain_id="test-chain")
        result = builder.build_send_tx(
            private_key_hex=PRIVATE_KEY_HEX,
            from_address="gonka1sender",
            to_address="gonka1receiver",
            amount=NanoGonkaCoinDto("1000"),
            account_number=0,
            sequence=0,
            fee_denom="custom_denom",
            fee_amount=500,
        )
        tx_raw = TxRawDto().parse(result)
        auth_info = AuthInfoDto().parse(tx_raw.auth_info_bytes)
        assert auth_info.fee.amount[0].denom == "custom_denom"
        assert auth_info.fee.amount[0].amount == "500"

    def test_empty_fee_denom_uses_amount_denom(self):
        builder = TxBuilder(chain_id="test-chain")
        result = builder.build_send_tx(
            private_key_hex=PRIVATE_KEY_HEX,
            from_address="gonka1sender",
            to_address="gonka1receiver",
            amount=CoinDto(denom="myfee", amount="1000"),
            account_number=0,
            sequence=0,
            fee_denom="",
        )
        tx_raw = TxRawDto().parse(result)
        auth_info = AuthInfoDto().parse(tx_raw.auth_info_bytes)
        assert auth_info.fee.amount[0].denom == "myfee"
