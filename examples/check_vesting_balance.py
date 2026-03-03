"""Example: query vesting balance for an address."""

from gonka_wallet import GonkaClient, DEFAULT_CHAIN_CONFIG, ngonka_to_gonka

ADDRESS = "gonka1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnrpw28"  # replace with real address

with GonkaClient(DEFAULT_CHAIN_CONFIG) as client:
    response = client.vesting_balance(ADDRESS)

print(f"Address: {response.address}")

if not response.balances:
    print("Vesting balance: empty (no vesting tokens)")
else:
    for coin in response.balances:
        if coin.denom == "ngonka":
            gonka = ngonka_to_gonka(int(coin.amount))
            print(f"  {coin.denom}: {coin.amount} ({gonka:.4f} GONKA)")
        else:
            print(f"  {coin.denom}: {coin.amount}")
