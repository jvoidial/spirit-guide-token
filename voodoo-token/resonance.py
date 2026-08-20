import math

# ---------- TOKEN PARAMETERS (you can edit these) ----------
SUPPLY = 100_000_000_000_000   # total supply (e.g., 100 trillion for VDOO)
DECIMALS = 18
BURN_PERCENT = 0.99            # 99% burn => remaining 1%
REMAINING_SUPPLY = SUPPLY * (1 - BURN_PERCENT)

# Liquidity pool parameters
INITIAL_LIQUIDITY_ETH = 0.1   # ETH you deposit (adjust as needed)
TARGET_PRICE_PER_TOKEN_ETH = 0.000000000001  # starting price after burn
TOKENS_FOR_LIQUIDITY = REMAINING_SUPPLY * 0.1  # 10% of remaining supply

# Holder growth assumptions
INITIAL_HOLDERS = 10
HOLDERS_AFTER_1_YEAR = 1000
PRICE_MULTIPLIER_PER_HOLDER = 1.02   # 2% price increase for each new holder

# Simulate price over time
def simulate():
    current_price = TARGET_PRICE_PER_TOKEN_ETH
    current_holders = INITIAL_HOLDERS
    month = 0
    print("\n🌌 Resonance Engine – Price Projection (post-burn)")
    print("=" * 60)
    print(f"Burned {BURN_PERCENT*100:.0f}% of supply. Remaining: {REMAINING_SUPPLY:,.0f} tokens")
    print(f"Starting price: {current_price:.15f} ETH per token")
    print("=" * 60)

    for month in range(0, 37, 3):   # print every 3 months for 3 years
        # price grows due to holder growth (viral coefficient)
        new_holders = INITIAL_HOLDERS * (1 + 0.05) ** month
        price_multiplier = PRICE_MULTIPLIER_PER_HOLDER ** (new_holders - current_holders)
        current_price *= price_multiplier

        # market cap = price * remaining_supply
        market_cap_eth = current_price * REMAINING_SUPPLY
        market_cap_usd = market_cap_eth * 2500  # assume 1 ETH = $2500

        print(f"Month {month:2d}: Holders~{int(new_holders):6d}  Price={current_price:.15f} ETH   MCap=${market_cap_usd:,.0f}")

    # show when you become a millionaire
    print("\n💰 Millionaire Threshold (if you own 10% of remaining supply):")
    your_share = REMAINING_SUPPLY * 0.1
    millionaire_price = 1_000_000 / (your_share * 2500)   # price in ETH
    print(f"You need price to reach {millionaire_price:.12f} ETH to have $1M.")
    print(f"At current growth rate, that might happen in ~{estimate_time(millionaire_price, current_price, PRICE_MULTIPLIER_PER_HOLDER)} months.")
    print("\n✨ The engine shows the path. Now you must walk it.")

def estimate_time(target_price, current_price, growth_factor):
    # rough estimate assuming exponential growth
    if target_price <= current_price:
        return 0
    return math.log(target_price / current_price) / math.log(growth_factor)

if __name__ == "__main__":
    simulate()
