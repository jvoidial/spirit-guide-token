#!/usr/bin/env python3
import os, sys, json
from web3 import Web3

def main():
    # ---- Get inputs ----
    token_addr = input("Enter token contract address: ").strip()
    sender = input("Enter your current wallet address (sender): ").strip()
    recipient = input("Enter recipient wallet address: ").strip()

    # Validate addresses
    if not Web3.is_address(token_addr) or not Web3.is_address(sender) or not Web3.is_address(recipient):
        print("❌ Invalid address format. Please check and re-run.")
        sys.exit(1)

    # ---- Connect to Base ----
    w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
    if not w3.is_connected():
        print("❌ RPC connection failed.")
        sys.exit(1)

    # ---- Minimal ABI for ERC-20 ----
    ERC20_ABI = [
        {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
    ]

    token = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)

    # ---- Fetch token info ----
    try:
        symbol = token.functions.symbol().call()
        decimals = token.functions.decimals().call()
    except Exception as e:
        print(f"❌ Failed to read token info: {e}")
        print("   Make sure the contract address is correct and is an ERC-20 token.")
        sys.exit(1)

    # ---- Check balances ----
    sender_bal = token.functions.balanceOf(Web3.to_checksum_address(sender)).call()
    recipient_bal = token.functions.balanceOf(Web3.to_checksum_address(recipient)).call()

    print("\n📊 TOKEN INFO:")
    print(f"   Symbol: {symbol}")
    print(f"   Decimals: {decimals}")
    print(f"   Contract: {token_addr}")

    print("\n💰 BALANCES:")
    print(f"   Sender: {sender_bal / 10**decimals} {symbol} (wei: {sender_bal})")
    print(f"   Recipient: {recipient_bal / 10**decimals} {symbol} (wei: {recipient_bal})")

    # ---- Check if recipient is a contract ----
    code = w3.eth.get_code(Web3.to_checksum_address(recipient))
    is_contract = len(code) > 0
    if is_contract:
        print("⚠️  Recipient is a contract – some contracts reject direct ERC-20 transfers.")
    else:
        print("✅ Recipient is an externally owned account (EOA) – transfers should work.")

    # ---- Simulate a transfer of 1 token (1e18 wei) ----
    if sender_bal >= 10**decimals:
        print("\n🧪 Simulating transfer of 1 token (wei: 10^{}) to recipient...".format(decimals))
        try:
            # Use call() to simulate without spending gas
            result = token.functions.transfer(
                Web3.to_checksum_address(recipient),
                10**decimals
            ).call({'from': Web3.to_checksum_address(sender)})
            print("✅ Simulation succeeded! The transfer should succeed.")
        except Exception as e:
            print("❌ Simulation failed with error:")
            print(f"   {e}")
            print("\n🔍 This usually means:")
            print("   • Insufficient balance (but we see balance, so not that)")
            print("   • The recipient is blacklisted (if token has blacklist)")
            print("   • The sender doesn't have allowance (if using transferFrom, but we are using transfer)")
            print("   • The token has a custom modifier (e.g., onlyWhitelisted) that rejects the transfer")
            print("   • The recipient is a contract that reverts on receive")
    else:
        print("⚠️  Sender balance is less than 1 token. Cannot simulate with 1 token.")

    # ---- Check if sender has enough balance for the intended full transfer ----
    # The user wanted to send the entire balance, so we check if the displayed amount is correct.
    # We'll just output the balance as we already did.

    print("\n📌 FINAL DIAGNOSIS:")
    if is_contract:
        print("   - Recipient is a contract. Consider sending to an EOA first, or check if the contract accepts ERC-20 tokens.")
    if sender_bal == 0:
        print("   - Sender has zero balance. You may have already sent the tokens, or the address is wrong.")
    elif sender_bal > 0:
        print("   - Sender has a balance. The failure might be due to the token contract's custom logic.")
        print("     Please check the contract's source code for any restrictions (e.g., blacklist, max transfer amount).")

    print("\n✅ Diagnostic complete.")
    print("You can now use this information to troubleshoot further.")

if __name__ == "__main__":
    main()
