#!/usr/bin/env python3
import os, requests, json, sys
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("BASE_SCAN_API_KEY")
if not API_KEY:
    print("❌ BASE_SCAN_API_KEY missing in .env")
    sys.exit(1)

SCAMMER = "0x6511204D46a83BfFcC0DB73d5358522C8307981e8"

def fetch_transactions(address, action="txlist", sort="desc"):
    url = "https://api.basescan.org/api"
    params = {
        "module": "account",
        "action": action,
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": sort,
        "apikey": API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data["status"] != "1":
            print(f"⚠️ API error for {action}: {data.get('message', 'Unknown')}")
            return []
        return data["result"]
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []

def get_all_addresses(transactions):
    addrs = set()
    for tx in transactions:
        if tx["from"].lower() != SCAMMER.lower():
            addrs.add(tx["from"])
        if tx["to"] and tx["to"].lower() != SCAMMER.lower():
            addrs.add(tx["to"])
    return addrs

def main():
    addrs = set()
    addrs.add(SCAMMER.lower())  # Always include the scammer

    print("🔍 Fetching ETH transactions...")
    txs = fetch_transactions(SCAMMER, action="txlist")
    if txs:
        addrs.update(get_all_addresses(txs))
        print(f"   Found {len(txs)} ETH transactions.")
    else:
        print("   No ETH transactions found or API error.")

    print("🔍 Fetching ERC20 token transfers...")
    token_txs = fetch_transactions(SCAMMER, action="tokentx")
    if token_txs:
        addrs.update(get_all_addresses(token_txs))
        print(f"   Found {len(token_txs)} token transfers.")
    else:
        print("   No token transfers found or API error.")

    # Save to file
    with open("scammer_network.txt", "w") as f:
        for addr in sorted(addrs):
            f.write(f"{addr}\n")

    print(f"✅ Total unique addresses: {len(addrs)}")
    # Preview first 10
    print("\n📋 First 10 addresses:")
    for i, addr in enumerate(sorted(addrs)):
        if i >= 10: break
        print(f"  - {addr}")

if __name__ == "__main__":
    main()
