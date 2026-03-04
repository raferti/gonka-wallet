"""Example: send tokens from one address to another."""

from gonka_wallet import GonkaClient, DEFAULT_CHAIN_CONFIG, gonka_to_ngonka
from gonka_wallet.dto.coin import GonkaCoinDto, NanoGonkaCoinDto
from gonka_wallet.exceptions.client import TransactionTimeout

# Replace these values before running
PRIVATE_KEY  = "your_private_key_hex_here"
FROM_ADDRESS = "gonka1..."
TO_ADDRESS   = "gonka1..."

# Amount to send
AMOUNT_GONKA = 1.0  # in GONKA

amount = GonkaCoinDto(amount=str(AMOUNT_GONKA))

# convert gonka to ngonka
# amount = NanoGonkaCoinDto(amount=str(gonka_to_ngonka(AMOUNT_GONKA)))

# Example: BROADCAST_MODE_SYNC (default)
# Node checks the tx before responding — is_success reflects the actual result.
with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    response = client.send(
        private_key=PRIVATE_KEY,
        from_address=FROM_ADDRESS,
        to_address=TO_ADDRESS,
        amount=amount,
        gas_limit=200_000,
        fee_amount=0,
        memo="sent via gonka_wallet",
    )

if response.is_success:
    print(f"Transaction sent!")
    print(f"  TX hash:  {response.tx_hash}")
    print(f"  From:     {response.from_address}")
    print(f"  To:       {response.to_address}")
    print(f"  Amount:   {response.amount} ngonka ({AMOUNT_GONKA} GONKA)")
else:
    print(f"Transaction failed (code={response.code}): {response.log}")
    if response.tx_hash:
        print(f"  TX hash: {response.tx_hash}")
    else:
        print("  TX was not accepted by the chain")

# Example 2: BROADCAST_MODE_ASYNC + wait_for_tx
# Node responds immediately without checking the tx.
# is_success is always True — use wait_for_tx to get the actual result.
with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    response = client.send(
        private_key=PRIVATE_KEY,
        from_address=FROM_ADDRESS,
        to_address=TO_ADDRESS,
        amount=amount,
        broadcast_mode="BROADCAST_MODE_ASYNC",
    )

    print(f"Transaction submitted: {response.tx_hash}")

    try:
        tx = client.wait_for_tx(response.tx_hash, timeout=60)
        tx_response = tx["tx_response"]
        if tx_response["code"] == 0:
            print(f"Confirmed in block {tx_response['height']}")
        else:
            print(f"Failed on chain (code={tx_response['code']}): {tx_response['raw_log']}")
    except TransactionTimeout:
        print(f"Timed out waiting for {response.tx_hash}")
