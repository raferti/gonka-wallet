from gonka_wallet.dto.coin import CoinDto, GonkaCoinDto, NanoGonkaCoinDto
from gonka_wallet.dto.response import BalanceResponseDto, BroadcastTxResponseDto, SendResponseDto


class TestCoinDto:
    def test_serialize_parse_round_trip(self):
        coin = CoinDto(denom="ngonka", amount="1000")
        raw = bytes(coin)
        parsed = CoinDto().parse(raw)
        assert parsed.denom == "ngonka"
        assert parsed.amount == "1000"

    def test_gonka_coin(self):
        coin = GonkaCoinDto("100")
        assert coin.denom == "gonka"
        assert coin.amount == "100"

    def test_nano_gonka_coin(self):
        coin = NanoGonkaCoinDto("100")
        assert coin.denom == "ngonka"
        assert coin.amount == "100"


class TestSendResponseDto:
    def test_error_factory(self):
        resp = SendResponseDto.error("from", "to", 100, 5, "fail")
        assert not resp.is_success
        assert resp.code == 5
        assert resp.tx_hash == ""
        assert resp.log == "fail"


class TestBalanceResponseDto:
    def test_is_empty(self):
        resp = BalanceResponseDto(address="gonka1abc", balances=[])
        assert resp.is_empty is True

    def test_not_empty(self):
        resp = BalanceResponseDto(
            address="gonka1abc",
            balances=[CoinDto(denom="ngonka", amount="100")],
        )
        assert resp.is_empty is False


class TestBroadcastTxResponseDto:
    def test_success(self):
        resp = BroadcastTxResponseDto(tx_hash="ABC", code=0, log="")
        assert resp.is_success is True

    def test_failure(self):
        resp = BroadcastTxResponseDto(tx_hash="", code=5, log="error")
        assert resp.is_success is False
