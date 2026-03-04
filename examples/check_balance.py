"""Example: query all token balances for an address."""

from gonka_wallet import GonkaClient, DEFAULT_CHAIN_CONFIG

ADDRESS = "gonka1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnrpw28"  # replace with real address

with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    try:
        response = client.balance(ADDRESS)
    # Handle standard network errors
    except Exception as e:
        print(e)

# Checking the response from the blockchain
if response.is_success:
    if response.balances:
        print(f"Address: {response.address} ")
        for coin in response.balances:
            print(f"{coin.amount} {coin.denom}")
    else:
        print(f"Balance is empty")
else:
    print(f"Query failed (code={response.code}): {response.log}")

