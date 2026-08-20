import math

# ---------- PARAMETERS ----------
SUPPLY = 1_000_000_000          # 1 billion tokens after mega burn
TARGET_PRICE = 1e-10            # 0.0000000001 ETH starting price
INITIAL_HOLDERS = 50
MONTHLY_HOLDER_GROWTH = 0.20   # 20% per month
PRICE_MULTIPLIER_PER_HOLDER = 1.05   # price multiplier for each new holder
YOUR_SHARE = 0.1                # you keep 10% of supply
ETH_USD = 2500

# ---------- SIMULATION ----------
current_price = TARGET_PRICE
current_holders = INITIAL_HOLDERS
month = 0

# Milestones in USD
milestones = [1e6, 1e9, 1e12, 1e15, 1e18, 1e21, 1e24, 1e27]
milestone_idx = 0
next_milestone = milestones[milestone_idx]

# Helper to calculate your wealth in USD
def your_wealth(price, supply_share, eth_usd):
    return price * supply_share * eth_usd

print("🌌 Resonance Engine — Eternal Wealth Timeline")
print("=" * 70)
print(f"Supply: {SUPPLY:,} tokens (post mega burn)")
print(f"Your share: {YOUR_SHARE*100:.0f}% = {SUPPLY*YOUR_SHARE:,.0f} tokens")
print(f"Starting price: {current_price:.15f} ETH")
print(f"Holders at month 0: {INITIAL_HOLDERS}")
print("=" * 70)

# Run until we've shown all milestones (or trillions of months)
while milestone_idx < len(milestones):
    month += 1
    # Holder growth
    new_holders = INITIAL_HOLDERS * ((1 + MONTHLY_HOLDER_GROWTH) ** month)
    # Price increase from additional holders
    additional_holders = new_holders - current_holders
    if additional_holders > 0:
        price_multiplier = PRICE_MULTIPLIER_PER_HOLDER ** additional_holders
    else:
        price_multiplier = 1.0
    current_price *= price_multiplier
    current_holders = new_holders

    # Check milestones
    wealth = your_wealth(current_price, SUPPLY * YOUR_SHARE, ETH_USD)
    if wealth >= next_milestone:
        # Format large numbers nicely
        if next_milestone < 1e15:
            milestone_str = f"${next_milestone:,.0f}"
        else:
            milestone_str = f"${next_milestone:.2e}"
        print(f"🏆 Month {month:,}: Reached {milestone_str}! Wealth = ${wealth:,.2f}")
        milestone_idx += 1
        if milestone_idx < len(milestones):
            next_milestone = milestones[milestone_idx]
    # Print progress every 100 months (optional, can be removed for faster run)
    if month % 100 == 0:
        print(f"   Month {month:,}: Holders~{int(current_holders):,}  Price={current_price:.2e} ETH  Wealth=${wealth:,.2f}")

print("\n✨ The engine has revealed all milestones. You now hold the map to eternity.")
