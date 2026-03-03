"""Example: send tokens from one address to another."""

from gonka_wallet import GonkaClient, DEFAULT_CHAIN_CONFIG, gonka_to_ngonka
from gonka_wallet.dto.coin import GonkaCoinDto, NanoGonkaCoinDto

# Replace these values before running
PRIVATE_KEY  = "your_private_key_hex_here"
FROM_ADDRESS = "gonka1..."
TO_ADDRESS   = "gonka1..."

# Amount to send
AMOUNT_GONKA = 1.0  # in GONKA

amount = GonkaCoinDto(amount=str(AMOUNT_GONKA))

# convert gonka to ngonka
# amount = NanoGonkaCoinDto(amount=str(gonka_to_ngonka(AMOUNT_GONKA)))

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
    print(f"Transaction failed!")
    print(f"  Code: {response.code}")
    print(f"  Log:  {response.log}")
