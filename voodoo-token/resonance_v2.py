import math

SUPPLY = 1_000_000_000  # 1 billion after mega burn
DECIMALS = 18
INITIAL_LIQUIDITY_ETH = 0.5
TARGET_PRICE_PER_TOKEN_ETH = 0.0000000001   # higher due to extreme scarcity
TOKENS_FOR_LIQUIDITY = SUPPLY * 0.1
INITIAL_HOLDERS = 50
MONTHLY_HOLDER_GROWTH = 0.20   # 20% monthly viral growth
PRICE_MULTIPLIER_PER_HOLDER = 1.05

current_price = TARGET_PRICE_PER_TOKEN_ETH
current_holders = INITIAL_HOLDERS

print("🌌 Resonance Engine V2 — Aggressive Path")
print("=" * 60)
print(f"Supply: {SUPPLY:,} tokens (post 99.999% burn)")
print(f"Starting price: {current_price:.15f} ETH per token")
print("=" * 60)

for month in range(0, 25, 3):
    new_holders = INITIAL_HOLDERS * ((1 + MONTHLY_HOLDER_GROWTH) ** month)
    price_multiplier = PRICE_MULTIPLIER_PER_HOLDER ** (new_holders - current_holders)
    current_price *= price_multiplier
    market_cap_eth = current_price * SUPPLY
    market_cap_usd = market_cap_eth * 2500
    print(f"Month {month:2d}: Holders~{int(new_holders):6d}  Price={current_price:.15f} ETH   MCap=${market_cap_usd:,.0f}")

your_share = SUPPLY * 0.1
millionaire_price = 1_000_000 / (your_share * 2500)
print(f"\n💰 To reach $1M with 10% of supply, need price: {millionaire_price:.12f} ETH")
print(f"Projected to achieve around month ~{estimate_time(millionaire_price, current_price, 1.05)}")
