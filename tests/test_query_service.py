import base64
from unittest.mock import MagicMock

import pytest

from gonka_wallet.client.query_service import GonkaQueryService, CODE_NOT_FOUND
from gonka_wallet.dto.coin import CoinDto
from gonka_wallet.dto.query import (
    BaseAccountDto,
    QueryAccountResponseDto,
    QueryAllBalancesResponseDto,
)
from gonka_wallet.dto.response import BroadcastTxResponseDto
from gonka_wallet.dto.transaction import PbAnyDto
from gonka_wallet.exceptions.client import AccountNotFoundError, TransactionNotFound


@pytest.fixture
def mock_transport():
    return MagicMock()


@pytest.fixture
def query_service(mock_transport):
    return GonkaQueryService(
        node_chain_rpc_url="http://localhost:26657",
        node_chain_api_url="http://localhost:1317",
        transport=mock_transport,
    )


@pytest.fixture
def query_service_no_api(mock_transport):
    return GonkaQueryService(
        node_chain_rpc_url="http://localhost:26657",
        node_chain_api_url="",
        transport=mock_transport,
    )


def _make_abci_response(code: int, value_bytes: bytes = b""):
    value_b64 = base64.b64encode(value_bytes).decode() if value_bytes else ""
    resp = {"result": {"response": {"code": code}}}
    if code == 0 and value_b64:
        resp["result"]["response"]["value"] = value_b64
    return resp


class TestQueryAllBalances:
    def test_decodes_balances(self, query_service, mock_transport):
        balances_resp = QueryAllBalancesResponseDto(
            balances=[CoinDto(denom="ngonka", amount="5000")]
        )
        mock_transport.get.return_value = _make_abci_response(0, bytes(balances_resp))

        result = query_service.query_all_balances("gonka1abc")
        assert len(result) == 1
        assert result[0].denom == "ngonka"
        assert result[0].amount == "5000"

    def test_empty_balances(self, query_service, mock_transport):
        mock_transport.get.return_value = _make_abci_response(22)
        result = query_service.query_all_balances("gonka1abc")
        assert result == []


class TestQueryAccount:
    def test_returns_account_info(self, query_service, mock_transport):
        account = BaseAccountDto(
            address="gonka1abc",
            pub_key=PbAnyDto(),
            account_number=42,
            sequence=7,
        )
        account_resp = QueryAccountResponseDto(
            account=PbAnyDto(type_url="/cosmos.auth.v1beta1.BaseAccount", value=bytes(account))
        )
        mock_transport.get.return_value = _make_abci_response(0, bytes(account_resp))

        acc_num, seq = query_service.query_account("gonka1abc")
        assert acc_num == 42
        assert seq == 7

    def test_not_found(self, query_service, mock_transport):
        mock_transport.get.return_value = _make_abci_response(CODE_NOT_FOUND)
        with pytest.raises(AccountNotFoundError):
            query_service.query_account("gonka1abc")


class TestBroadcastTx:
    def test_returns_response(self, query_service, mock_transport):
        mock_transport.post.return_value = {
            "tx_response": {"txhash": "ABC123", "code": 0, "raw_log": ""}
        }
        result = query_service.broadcast_tx(b"tx_bytes")
        assert isinstance(result, BroadcastTxResponseDto)
        assert result.tx_hash == "ABC123"
        assert result.is_success

    def test_no_api_url(self, query_service_no_api):
        with pytest.raises(ValueError, match="node_chain_api_url"):
            query_service_no_api.broadcast_tx(b"tx_bytes")


class TestGetTx:
    def test_returns_dict(self, query_service, mock_transport):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tx": "data"}
        mock_transport.get_raw.return_value = mock_response

        result = query_service.get_tx("HASH123")
        assert result == {"tx": "data"}

    def test_not_found(self, query_service, mock_transport):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_transport.get_raw.return_value = mock_response

        with pytest.raises(TransactionNotFound):
            query_service.get_tx("HASH123")


class TestQueryTotalVesting:
    def test_parses_total_amount(self, query_service, mock_transport):
        mock_transport.get.return_value = {
            "total_amount": [{"denom": "ngonka", "amount": "3000"}]
        }
        result = query_service.query_total_vesting("gonka1abc")
        assert len(result) == 1
        assert result[0].denom == "ngonka"
        assert result[0].amount == "3000"


class TestClose:
    def test_closes_transport(self, query_service, mock_transport):
        query_service.close()
        mock_transport.close.assert_called_once()
