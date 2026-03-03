"""Cosmos SDK query service: protobuf encode/decode, ABCI paths, REST endpoints."""

import base64
from typing import Literal

from .transport import HttpTransport
from ..dto.coin import CoinDto
from ..dto.query import (
    BaseAccountDto,
    QueryAccountRequestDto,
    QueryAccountResponseDto,
    QueryAllBalancesRequestDto,
    QueryAllBalancesResponseDto,
)
from ..dto.response import BroadcastTxResponseDto
from ..exceptions.client import AccountNotFoundError, TransactionNotFound

ABCI_PATH_ALL_BALANCES = "/cosmos.bank.v1beta1.Query/AllBalances"
ABCI_PATH_ACCOUNT = "/cosmos.auth.v1beta1.Query/Account"

# ABCI response code for "not found"
CODE_NOT_FOUND = 22


class GonkaQueryService:
    """Knows about Cosmos SDK: ABCI query encoding, protobuf, REST API endpoints."""

    def __init__(self, node_chain_rpc_url: str, node_chain_api_url: str = "", timeout: int = 60, transport: HttpTransport = None):
        self._node_chain_rpc_url = node_chain_rpc_url
        self._node_chain_api_url = node_chain_api_url.rstrip("/") if node_chain_api_url else ""
        self._transport = transport or HttpTransport(timeout=timeout)

    def close(self):
        self._transport.close()

    def query_all_balances(self, address: str) -> list[CoinDto]:
        """Protobuf encode -> ABCI query -> protobuf decode. Returns list of coins."""
        request = QueryAllBalancesRequestDto(address=address)
        data_hex = "0x" + bytes(request).hex()

        code, value = self._abci_query(ABCI_PATH_ALL_BALANCES, data_hex)

        if code != 0 or not value:
            return []

        resp = QueryAllBalancesResponseDto().parse(value)
        return resp.balances or []

    def query_account(self, address: str) -> tuple[int, int]:
        """Returns (account_number, sequence). Raises AccountNotFoundError if not found."""
        req = QueryAccountRequestDto(address=address)
        data_hex = "0x" + bytes(req).hex()

        code, value = self._abci_query(ABCI_PATH_ACCOUNT, data_hex)

        if code != 0:
            if code == CODE_NOT_FOUND:
                raise AccountNotFoundError(
                    f"Account not found on chain. Fund the address first: {address}"
                )
            raise AccountNotFoundError(f"Account query failed (code={code})")

        account_number = 0
        sequence = 0
        if value:
            resp = QueryAccountResponseDto().parse(value)
            acc = BaseAccountDto().parse(resp.account.value)
            account_number = acc.account_number
            sequence = acc.sequence

        return account_number, sequence

    def broadcast_tx(
            self,
            tx_bytes: bytes,
            broadcast_mode: Literal[
                "BROADCAST_MODE_SYNC",
                "BROADCAST_MODE_ASYNC"] = "BROADCAST_MODE_SYNC"
    ) -> BroadcastTxResponseDto:
        """POST to REST API /cosmos/tx/v1beta1/txs."""
        if not self._node_chain_api_url:
            raise ValueError("node_chain_api_url is required for broadcast_tx")

        url = f"{self._node_chain_api_url}/cosmos/tx/v1beta1/txs"
        tx_b64 = base64.b64encode(tx_bytes).decode()
        payload = {"tx_bytes": tx_b64, "mode": broadcast_mode}

        data = self._transport.post(url, payload)

        tx_response = data["tx_response"]
        return BroadcastTxResponseDto(
            tx_hash=tx_response["txhash"],
            code=tx_response.get("code", 0),
            log=tx_response.get("raw_log", ""),
        )

    def get_tx(self, tx_hash: str) -> dict:
        """GET from REST API /cosmos/tx/v1beta1/txs/{hash}.

        Raises TransactionNotFound if the transaction is not yet on chain.
        """

        if not self._node_chain_api_url:
            raise ValueError("node_chain_api_url is required for get_tx")

        url = f"{self._node_chain_api_url}/cosmos/tx/v1beta1/txs/{tx_hash}"
        response = self._transport.get_raw(url)

        if response.status_code != 200:
            raise TransactionNotFound(f"Transaction {tx_hash} not found")

        return response.json()

    def query_total_vesting(self, address: str) -> list[CoinDto]:
        """GET total vesting for an address. Returns list of coins."""
        if not self._node_chain_api_url:
            raise ValueError("node_chain_api_url is required for query_total_vesting")

        url = f"{self._node_chain_api_url}/productscience/inference/streamvesting/total_vesting/{address}"
        data = self._transport.get(url)
        return [CoinDto(denom=c["denom"], amount=c["amount"]) for c in data.get("total_amount", [])]

    def _abci_query(self, path: str, data_hex: str) -> tuple[int, bytes]:
        """Send ABCI query via RPC. Returns (code, value_bytes)."""
        url = f"{self._node_chain_rpc_url}/abci_query"
        params = {"path": f'"{path}"', "data": data_hex}

        result = self._transport.get(url, params=params)

        abci_resp = result["result"]["response"]
        code = abci_resp.get("code", 0)

        value = b""
        if code == 0:
            value_b64 = abci_resp.get("value")
            if value_b64:
                value = base64.b64decode(value_b64)

        return code, value
