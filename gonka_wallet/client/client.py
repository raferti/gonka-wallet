"""Gonka network client: balance queries and transaction broadcasting."""

import time
from typing import Literal

import bech32

from .query_service import GonkaQueryService
from ..config import ChainConfig
from ..dto.coin import CoinDto
from ..dto.response import BalanceResponseDto, SendResponseDto
from ..exceptions.client import AccountNotFoundError, TransactionNotFound, TransactionTimeout
from ..tx.builder import TxBuilder


class GonkaClient:
    """Network client for a Gonka chain. Pure business logic."""

    def __init__(
            self,
            config: ChainConfig,
            timeout: int = 60,
            query_service: GonkaQueryService = None
    ):
        self._config = config
        self._query = query_service or GonkaQueryService(
            node_chain_rpc_url=config.node_chain_rpc_url,
            node_chain_api_url=config.node_chain_api_url,
            timeout=timeout,
        )

    def close(self):
        self._query.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def balance(self, address: str) -> BalanceResponseDto:
        """Query all balances for an address."""
        balances = self._query.query_all_balances(address)
        return BalanceResponseDto(address=address, balances=balances)

    def send(
        self, private_key: str, from_address: str, to_address: str, amount: CoinDto,
        gas_limit: int = 200_000, fee_amount: int = 0, memo: str = "",
        broadcast_mode: Literal["BROADCAST_MODE_SYNC", "BROADCAST_MODE_ASYNC"] = "BROADCAST_MODE_SYNC",
    ) -> SendResponseDto:
        """Build, sign and broadcast a MsgSend transaction."""
        _validate_bech32_address(from_address)
        _validate_bech32_address(to_address)

        try:
            account_number, sequence = self._query.query_account(from_address)
        except AccountNotFoundError as e:
            return SendResponseDto.error(from_address, to_address, int(amount.amount), 22, str(e))

        tx_builder = TxBuilder(chain_id=self._config.chain_id)
        transaction_bytes = tx_builder.build_send_tx(
            private_key_hex=private_key,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            account_number=account_number,
            sequence=sequence,
            gas_limit=gas_limit,
            fee_amount=fee_amount,
            fee_denom=self._config.fee_denom,
            memo=memo,
        )

        broadcast_response = self._query.broadcast_tx(transaction_bytes, broadcast_mode)

        amount_int = int(amount.amount)

        if not broadcast_response.is_success:
            return SendResponseDto.error(
                from_address, to_address, amount_int,
                broadcast_response.code, broadcast_response.log,
            )

        return SendResponseDto(
            tx_hash=broadcast_response.tx_hash,
            from_address=from_address,
            to_address=to_address,
            amount=amount_int,
        )

    def vesting_balance(self, address: str) -> BalanceResponseDto:
        """Query total vesting balance for an address."""
        balances = self._query.query_total_vesting(address)
        return BalanceResponseDto(address=address, balances=balances)

    def get_tx(self, tx_hash: str) -> dict:
        """Query a transaction by hash."""
        return self._query.get_tx(tx_hash)

    def wait_for_tx(self, tx_hash: str, timeout: float = 60, poll_period: float = 5) -> dict:
        """Poll until a transaction appears on chain.

        Raises TransactionTimeout if not found within timeout.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                return self._query.get_tx(tx_hash)
            except TransactionNotFound:
                time.sleep(poll_period)

        raise TransactionTimeout(
            f"Transaction {tx_hash} not found on chain within {timeout}s"
        )


def _validate_bech32_address(address: str) -> None:
    """Validate bech32 address format. Raises ValueError if invalid."""
    hrp, data = bech32.bech32_decode(address)
    if hrp is None or data is None:
        raise ValueError(f"Invalid bech32 address: {address}")
