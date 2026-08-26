#!/usr/bin/env python3
import os, time, json, requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("BASE_SCAN_API_KEY")
if not API_KEY:
    print("❌ No API key. Exiting.")
    exit(1)

BASE_URL = "https://api.basescan.org/api"
LOG_FILE = "sweeper_world.log"
STATE_FILE = "sweeper_state.json"
WATCHLIST_FILE = "watchlist.txt"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def fetch_transactions(address, action="txlist", sort="desc", limit=20):
    params = {
        "module": "account",
        "action": action,
        "address": address,
        "sort": sort,
        "apikey": API_KEY,
        "startblock": 0,
        "endblock": 99999999
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()
        if data["status"] == "1":
            return data["result"][:limit]
        return []
    except:
        return []

def is_sweeper_pattern(address, tx_hash=None):
    # Get last 10 transactions (including internal and token)
    txs = fetch_transactions(address, action="txlist", limit=10)
    if not txs:
        return False
    # Check if there are multiple outgoing transactions within short time (e.g., 5 blocks)
    # Simple heuristic: if at least 3 outgoing transactions in the last 5 txs
    outgoing = 0
    for tx in txs:
        if tx["from"].lower() == address.lower():
            outgoing += 1
    return outgoing >= 3

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"watchlist": [], "last_tx": {}}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_initial_watchlist():
    # Load from scammer_network.txt if exists
    addrs = []
    if os.path.exists("scammer_network.txt"):
        with open("scammer_network.txt", "r") as f:
            addrs = [line.strip().lower() for line in f if line.strip()]
    # Also include the main scammer
    main = "0x6511204d46a83bffcc0db73d5358522c8307981e8".lower()
    if main not in addrs:
        addrs.append(main)
    return addrs

def main():
    log("🌍 Worldwide sweeper tracker started.")
    state = load_state()
    # Initialize watchlist from file + state
    watchlist = set(state.get("watchlist", []))
    # Add initial known addresses
    initial = load_initial_watchlist()
    watchlist.update(initial)
    # Also track any addresses from state's last_tx keys
    watchlist.update(state.get("last_tx", {}).keys())
    state["watchlist"] = list(watchlist)
    save_state(state)
    log(f"📋 Initial watchlist size: {len(watchlist)}")

    while True:
        new_addrs = set()
        for wallet in list(watchlist):
            # Fetch recent transactions
            txs = fetch_transactions(wallet, action="txlist", limit=5)
            if not txs:
                continue
            # Check last seen hash
            last_hash = state.get("last_tx", {}).get(wallet, "")
            new_txs = []
            for tx in txs:
                if tx["hash"] == last_hash:
                    break
                new_txs.append(tx)
            if new_txs:
                # Process new transactions (oldest first)
                for tx in reversed(new_txs):
                    log(f"📥 Tx {tx['hash']} for {wallet}")
                    log(f"   From: {tx['from']} -> To: {tx['to']} | Value: {int(tx['value'])/1e18} ETH")
                    # Check if this is an incoming tx to the watched wallet
                    if tx["to"].lower() == wallet.lower():
                        # Sender might be a sweeper
                        sender = tx["from"].lower()
                        if sender not in watchlist:
                            # Check if sender exhibits sweeper pattern
                            if is_sweeper_pattern(sender):
                                log(f"⚠️  SWEEPER DISCOVERED: {sender} (sweeps funds quickly)")
                                new_addrs.add(sender)
                            else:
                                # Still add to watchlist if it's not already? We'll add only if pattern.
                                pass
                    # If outgoing from watched wallet, flag as sweeper activity
                    if tx["from"].lower() == wallet.lower():
                        log(f"⚠️  OUTGOING from watched wallet – potential sweeper activity")
                # Update last seen hash
                state["last_tx"][wallet] = txs[0]["hash"]
        # Add newly discovered sweepers to watchlist
        if new_addrs:
            watchlist.update(new_addrs)
            state["watchlist"] = list(watchlist)
            log(f"➕ Added {len(new_addrs)} new sweepers to watchlist")
            # Optionally, save them to a file for persistent tracking
            with open("discovered_sweepers.txt", "a") as f:
                for addr in new_addrs:
                    f.write(f"{addr}\n")
        save_state(state)
        # Also load any new addresses from scammer_network.txt (in case it was updated)
        fresh = load_initial_watchlist()
        watchlist.update(fresh)
        state["watchlist"] = list(watchlist)
        save_state(state)

        time.sleep(60)  # Adjust to 30 sec if you have a high-rate API key

if __name__ == "__main__":
    main()
