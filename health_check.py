#!/usr/bin/env python3
import subprocess, json, requests, time, os, sys
from datetime import datetime, timedelta
from web3 import Web3

# ─── Configuration ────────────────────────────────────────────────
TOKENS = {
    "SGUIDE": "0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a",
    "VDOO": "0x38e4f08D08b4D772A7B75669C356b4749dd2d30b",
    "PENNIES": "0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7",
    "PIDX": "0xa36E026FC453880537e10d21fC139439bD2702fc"
}
RPC_URL = "https://base.llamarpc.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# ─── 1. Check processes ──────────────────────────────────────────
def check_process(name):
    result = subprocess.run(['pgrep', '-f', name], stdout=subprocess.PIPE)
    return result.returncode == 0

print("📡 ECOSYSTEM HEALTH CHECK")
print("=" * 40)

# ─── 2. Check master controller and sync watcher ──────────────
ctrl_ok = check_process('master_controller.py')
sync_ok = check_process('sync_investment_strategy.sh')
print(f"Master Controller: {'✅ RUNNING' if ctrl_ok else '❌ STOPPED'}")
print(f"Sync Watcher:      {'✅ RUNNING' if sync_ok else '❌ STOPPED'}")

# ─── 3. Check latest strategy JSON ──────────────────────────────
try:
    r = requests.get('https://jvoidial.github.io/spirit-guide-token/investment_strategy.json', timeout=5)
    if r.status_code == 200:
        data = r.json()
        ts = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        age = (datetime.now().astimezone() - ts).total_seconds()
        print(f"Strategy JSON:     ✅ Up to date (age: {int(age)}s, max 120s)" if age < 120 else f"⚠️  Stale (age: {int(age)}s)")
        # extract signals
        signals = data.get('investment_signals', {})
        for tok, sig in signals.items():
            print(f"   {tok}: {sig['action']} (conf {sig['confidence']}%) alloc {sig['allocation']}%")
    else:
        print("Strategy JSON:     ❌ Unreachable (HTTP", r.status_code, ")")
except Exception as e:
    print("Strategy JSON:     ❌ Error:", str(e))

# ─── 4. Fetch live prices from DexScreener ──────────────────────
print("\n📊 LIVE PRICES & LIQUIDITY")
addresses = ",".join(TOKENS.values())
try:
    r = requests.get(f'https://api.dexscreener.com/latest/dex/tokens/{addresses}', timeout=10)
    if r.status_code == 200:
        pairs = r.json().get('pairs', [])
        # group by token
        price_data = {}
        for pair in pairs:
            token_addr = pair.get('baseToken', {}).get('address', '').lower()
            for name, addr in TOKENS.items():
                if addr.lower() == token_addr:
                    price_data[name] = {
                        'price_usd': float(pair.get('priceUsd', 0)),
                        'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0))
                    }
                    break
        for name in TOKENS:
            if name in price_data:
                p = price_data[name]
                print(f"{name:8} ${p['price_usd']:,.10f}  liq: ${p['liquidity_usd']:,.2f}  24h vol: ${p['volume_24h']:,.2f}")
            else:
                print(f"{name:8} ❌ No price data")
    else:
        print("DexScreener API:  ❌ HTTP", r.status_code)
except Exception as e:
    print("DexScreener API:  ❌", str(e))

# ─── 5. Check contract verification via Sourcify ──────────────
print("\n🔍 CONTRACT VERIFICATION (Sourcify)")
for name, addr in TOKENS.items():
    try:
        r = requests.get(f'https://sourcify.dev/api/verification/status?address={addr}&chain=8453', timeout=5)
        if r.status_code == 200:
            status = r.json().get('status', 'unknown')
            print(f"{name:8} {'✅ VERIFIED' if status == 'VERIFIED' else '⚠️ ' + status}")
        else:
            print(f"{name:8} ❌ API error")
    except:
        print(f"{name:8} ❌ Connection error")

# ─── 6. Check website availability ──────────────────────────────
try:
    r = requests.get('https://jvoidial.github.io/spirit-guide-token/', timeout=5)
    print("\n🌐 Website:          ✅ Reachable" if r.status_code == 200 else f"❌ HTTP {r.status_code}")
except:
    print("\n🌐 Website:          ❌ Unreachable")

# ─── 7. Quick tip if anything is down ────────────────────────────
print("\n" + "=" * 40)
if not ctrl_ok:
    print("⚠️  Master controller is not running. Restart with:\n   cd ~/phb-ai-os_temp/spirit-guide-token && nohup python3 master_controller.py > controller.log 2>&1 &")
if not sync_ok:
    print("⚠️  Sync watcher is not running. Restart with:\n   cd ~/phb-ai-os_temp/spirit-guide-token && nohup ./sync_investment_strategy.sh > sync.log 2>&1 &")
print("✅ Health check complete.")
