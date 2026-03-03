from unittest.mock import MagicMock

import pytest

from gonka_wallet.client.client import GonkaClient
from gonka_wallet.dto.coin import CoinDto, NanoGonkaCoinDto
from gonka_wallet.dto.response import BalanceResponseDto, BroadcastTxResponseDto, SendResponseDto
from gonka_wallet.exceptions.client import AccountNotFoundError, TransactionNotFound, TransactionTimeout


@pytest.fixture
def mock_query():
    return MagicMock()


@pytest.fixture
def client(chain_config, mock_query):
    return GonkaClient(config=chain_config, query_service=mock_query)


@pytest.fixture
def sender_address(wallet):
    return wallet.address


@pytest.fixture
def receiver_address(chain_config):
    from gonka_wallet.wallet import Wallet
    w = Wallet.create_new(config=chain_config)
    return w.address


class TestBalance:
    def test_returns_balance_response(self, client, mock_query):
        coins = [CoinDto(denom="ngonka", amount="1000")]
        mock_query.query_all_balances.return_value = coins

        result = client.balance("gonka1abc")
        assert isinstance(result, BalanceResponseDto)
        assert result.address == "gonka1abc"
        assert result.balances == coins
        mock_query.query_all_balances.assert_called_once_with("gonka1abc")


class TestVestingBalance:
    def test_returns_balance_response(self, client, mock_query):
        coins = [CoinDto(denom="ngonka", amount="2000")]
        mock_query.query_total_vesting.return_value = coins

        result = client.vesting_balance("gonka1abc")
        assert isinstance(result, BalanceResponseDto)
        assert result.balances == coins
        mock_query.query_total_vesting.assert_called_once_with("gonka1abc")


class TestSend:
    def test_success(self, client, mock_query, known_private_key, sender_address, receiver_address):
        mock_query.query_account.return_value = (0, 0)
        mock_query.broadcast_tx.return_value = BroadcastTxResponseDto(
            tx_hash="ABCD1234", code=0, log=""
        )

        result = client.send(
            private_key=known_private_key,
            from_address=sender_address,
            to_address=receiver_address,
            amount=NanoGonkaCoinDto("1000"),
        )
        assert isinstance(result, SendResponseDto)
        assert result.is_success
        assert result.tx_hash == "ABCD1234"

    def test_broadcast_error(self, client, mock_query, known_private_key, sender_address, receiver_address):
        mock_query.query_account.return_value = (0, 0)
        mock_query.broadcast_tx.return_value = BroadcastTxResponseDto(
            tx_hash="", code=5, log="insufficient funds"
        )

        result = client.send(
            private_key=known_private_key,
            from_address=sender_address,
            to_address=receiver_address,
            amount=NanoGonkaCoinDto("1000"),
        )
        assert not result.is_success
        assert result.code == 5

    def test_account_not_found(self, client, mock_query, known_private_key, sender_address, receiver_address):
        mock_query.query_account.side_effect = AccountNotFoundError("not found")

        result = client.send(
            private_key=known_private_key,
            from_address=sender_address,
            to_address=receiver_address,
            amount=NanoGonkaCoinDto("1000"),
        )
        assert not result.is_success
        assert "not found" in result.log

    def test_invalid_address(self, client, known_private_key, receiver_address):
        with pytest.raises(ValueError, match="Invalid bech32"):
            client.send(
                private_key=known_private_key,
                from_address="invalid_address",
                to_address=receiver_address,
                amount=NanoGonkaCoinDto("1000"),
            )


class TestGetTx:
    def test_proxies_to_query(self, client, mock_query):
        mock_query.get_tx.return_value = {"tx": "data"}
        result = client.get_tx("HASH123")
        assert result == {"tx": "data"}
        mock_query.get_tx.assert_called_once_with("HASH123")


class TestWaitForTx:
    def test_finds_tx(self, client, mock_query):
        mock_query.get_tx.return_value = {"tx": "found"}
        result = client.wait_for_tx("HASH", timeout=5, poll_period=0.1)
        assert result == {"tx": "found"}

    def test_timeout(self, client, mock_query):
        mock_query.get_tx.side_effect = TransactionNotFound("not found")
        with pytest.raises(TransactionTimeout):
            client.wait_for_tx("HASH", timeout=0.2, poll_period=0.05)


class TestContextManager:
    def test_close_called(self, chain_config, mock_query):
        with GonkaClient(config=chain_config, query_service=mock_query) as c:
            pass
        mock_query.close.assert_called_once()
