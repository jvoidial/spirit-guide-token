#!/bin/bash
set -e

echo "🤖 Deploying Robot Contracts to Base..."

# Deploy Grid Trading Contract
echo "📦 Deploying GridTradingBot..."
forge create src/SGUIDE_ERC20.sol:SpiritGuide \
  --rpc-url https://mainnet.base.org \
  --private-key $PRIVATE_KEY \
  --broadcast

# Update the executor with contract addresses
echo "✅ Robot deployed! Update agi_executor.py with contract addresses."
