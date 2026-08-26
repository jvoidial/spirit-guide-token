#!/bin/bash
set -e

echo "🛡️ FULL SCAMMER NETWORK BLOCKER – AUTO"
echo "========================================"
echo "This script will:"
echo "  • Install Python packages (if needed)"
echo "  • Fetch all scammer-associated addresses via BaseScan"
echo "  • Update index.html with blacklist"
echo "  • Push to GitHub Pages"
echo ""

cd ~/phb-ai-os_temp/spirit-guide-token || exit 1

# ---- Ensure .env exists ----
if [ ! -f .env ]; then
    touch .env
fi

# ---- Check for BASE_SCAN_API_KEY ----
if ! grep -q "BASE_SCAN_API_KEY" .env; then
    echo ""
    read -p "🔑 Enter your BaseScan API key: " API_KEY
    echo "BASE_SCAN_API_KEY=$API_KEY" >> .env
    echo "✅ API key saved to .env"
fi

# ---- Install Python packages ----
echo "📦 Installing Python packages..."
pip install requests python-dotenv -q

# ---- Create the Python scanner script ----
cat > fetch_scammer_network.py << 'PY'
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
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    if data["status"] != "1":
        return []
    return data["result"]

def get_all_addresses(transactions):
    addrs = set()
    for tx in transactions:
        if tx["from"].lower() != SCAMMER.lower():
            addrs.add(tx["from"])
        if tx["to"] and tx["to"].lower() != SCAMMER.lower():
            addrs.add(tx["to"])
    return addrs

def main():
    print("🔍 Fetching ETH transactions for scammer...")
    txs = fetch_transactions(SCAMMER, action="txlist")
    addrs = get_all_addresses(txs)
    print("🔍 Fetching ERC20 token transfers...")
    token_txs = fetch_transactions(SCAMMER, action="tokentx")
    addrs.update(get_all_addresses(token_txs))
    addrs.add(SCAMMER.lower())
    with open("scammer_network.txt", "w") as f:
        for addr in sorted(addrs):
            f.write(f"{addr}\n")
    print(f"✅ Found {len(addrs)} unique addresses. Saved to scammer_network.txt")
    # Preview first 10
    print("\n📋 First 10 addresses:")
    for i, addr in enumerate(sorted(addrs)):
        if i >= 10: break
        print(f"  - {addr}")
PY

chmod +x fetch_scammer_network.py

# ---- Run the scanner ----
echo "🚀 Running scanner..."
python3 fetch_scammer_network.py

# ---- Build blacklist ----
if [ ! -f scammer_network.txt ]; then
    echo "❌ scammer_network.txt not found. Aborting."
    exit 1
fi

BLACKLIST_JS="const BLACKLIST = ["
while IFS= read -r addr; do
    BLACKLIST_JS+="\n  \"$addr\","
done < scammer_network.txt
BLACKLIST_JS="${BLACKLIST_JS%,}"
BLACKLIST_JS+="\n];"

# ---- Update index.html ----
cat > index.html << HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Spirit Guide – Secure</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#0a0a0a; color:#fff; font-family:'Segoe UI',sans-serif; min-height:100vh; display:flex; align-items:center; justify-content:center; }
    .container { max-width:800px; margin:auto; background:#1a1a1a; padding:2rem; border-radius:24px; border:1px solid #333; text-align:center; }
    .btn { background:#4fc3f7; color:#000; padding:0.7rem 1.5rem; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:1rem; }
    .blocked { background:#ff0000; color:#fff; height:100vh; width:100vw; display:flex; flex-direction:column; align-items:center; justify-content:center; font-size:3rem; text-align:center; }
    .blocked span { font-size:1.5rem; margin-top:1rem; }
    #walletDisplay { margin-top:1rem; word-break:break-all; color:#aaa; }
  </style>
</head>
<body>
  <div id="app">
    <div class="container">
      <h1>🌀 Spirit Guide Token</h1>
      <p style="color:#aaa;">Connect your wallet to continue.</p>
      <button class="btn" id="connectBtn">Connect Wallet</button>
      <div id="walletDisplay"></div>
    </div>
  </div>

  <script>
    $BLACKLIST_JS

    function kickScammer() {
      if (!window.ethereum) return;
      window.ethereum.request({ method: 'eth_accounts' })
        .then(accounts => {
          if (accounts.length > 0) {
            const connected = accounts[0].toLowerCase();
            if (BLACKLIST.includes(connected)) {
              document.body.innerHTML = \`
                <div class="blocked">
                  ⛔ ACCESS DENIED<br>
                  <span>Your wallet is blacklisted.</span>
                </div>
              \`;
            }
          }
        })
        .catch(() => {});
    }

    kickScammer();
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', kickScammer);
    }

    document.getElementById('connectBtn')?.addEventListener('click', async () => {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        document.getElementById('walletDisplay').innerText = 'Connected: ' + accounts[0];
        kickScammer();
      } catch (e) {
        alert('Connection failed.');
      }
    });
  </script>
</body>
</html>
HTML

echo "✅ index.html updated with $(wc -l < scammer_network.txt) blacklisted addresses."

# ---- Push to GitHub ----
echo "📤 Pushing to GitHub..."
git add index.html scammer_network.txt
git commit -m "Auto-block scammer network" || echo "ℹ️ No changes"
git push origin main || { echo "❌ Push failed."; exit 1; }

echo ""
echo "==========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "==========================================="
echo "🔗 Your site: https://jvoidial.github.io/spirit-guide-token/"
echo "🛡️ Blocking $(wc -l < scammer_network.txt) unique addresses."
echo "==========================================="
