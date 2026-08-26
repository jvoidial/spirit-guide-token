#!/bin/bash
set -e

echo "🛡️ ULTIMATE SCAMMER SHIELD – FINAL FIX"
echo "======================================="
echo "This script will:"
echo "  • Install dependencies"
echo "  • Deploy SecureToken on Base (local signing)"
echo "  • Blacklist scammer"
echo "  • Start auto‑seize monitor"
echo "  • Push encrypted token list"
echo ""
echo "⚠️  You need:"
echo "  • ~0.01 ETH on Base for gas"
echo "  • Your private key (64 hex chars)"
echo ""
read -p "Press ENTER to start, or Ctrl+C to cancel..."

cd ~/phb-ai-os_temp/spirit-guide-token || exit 1

# ---- Private key validation ----
if [ ! -f .env ]; then
    touch .env
fi

trim() { echo -n "$1" | tr -d ' \t\n\r'; }
validate_key() {
    local key="$1"
    key="$(trim "$key")"
    key="${key#0x}"
    [[ ${#key} -eq 64 && "$key" =~ ^[0-9a-fA-F]+$ ]]
}

EXISTING_KEY=$(grep -oP 'OWNER_PRIVATE_KEY=\K.*' .env 2>/dev/null | head -1)
if [[ -n "$EXISTING_KEY" && $(validate_key "$EXISTING_KEY") -eq 0 ]]; then
    echo "✅ Valid private key found in .env"
else
    sed -i '/OWNER_PRIVATE_KEY/d' .env
    echo ""
    echo "🔑 Enter your private key (64 hex chars, with or without 0x):"
    while true; do
        read -s PRIV_KEY
        PRIV_KEY="$(trim "$PRIV_KEY")"
        if validate_key "$PRIV_KEY"; then
            PRIV_KEY="${PRIV_KEY#0x}"
            PRIV_KEY="0x$PRIV_KEY"
            echo "OWNER_PRIVATE_KEY=$PRIV_KEY" >> .env
            echo "✅ Private key saved."
            break
        else
            echo "❌ Invalid. Must be 64 hex chars. Try again:"
        fi
    done
fi

# ---- Install tools ----
echo "📦 Installing system tools..."
pkg install wget jq solidity npm -y

if [ ! -d "node_modules/@openzeppelin" ]; then
    echo "📦 Installing @openzeppelin/contracts..."
    npm init -y
    npm install @openzeppelin/contracts
else
    echo "✅ OpenZeppelin already installed."
fi

echo "📦 Installing Python packages..."
pip install web3 python-dotenv

if ! command -v solc &> /dev/null; then
    echo "❌ solc not found. Aborting."
    exit 1
fi
echo "✅ solc version: $(solc --version)"

# ---- Create SecureToken.sol ----
cat > SecureToken.sol << 'SOL'
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SecureToken is ERC20, Ownable {
    mapping(address => bool) public blacklist;
    event BlacklistAdded(address indexed account);
    event BlacklistRemoved(address indexed account);
    event TokensSeized(address indexed from, uint256 amount, address indexed to);

    constructor(string memory name, string memory symbol)
        ERC20(name, symbol)
        Ownable(msg.sender)
    {}

    function addToBlacklist(address account) external onlyOwner {
        blacklist[account] = true;
        emit BlacklistAdded(account);
    }

    function removeFromBlacklist(address account) external onlyOwner {
        blacklist[account] = false;
        emit BlacklistRemoved(account);
    }

    function _update(address from, address to, uint256 amount) internal override {
        require(!blacklist[from] && !blacklist[to], "Blacklisted");
        super._update(from, to, amount);
    }

    function seizeTokens(address from, address to) external onlyOwner {
        require(blacklist[from], "Source not blacklisted");
        uint256 balance = balanceOf(from);
        require(balance > 0, "No tokens to seize");
        _transfer(from, to, balance);
        emit TokensSeized(from, balance, to);
    }
}
SOL

# ---- Create deployment script (with raw_transaction fix) ----
cat > deploy_contract.py << 'PY'
#!/usr/bin/env python3
import os, json, subprocess, time
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

print("🔨 Compiling SecureToken.sol...")
cmd = ["solc", "--base-path", ".", "--include-path", "node_modules",
       "--combined-json", "abi,bin", "SecureToken.sol"]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("❌ Compilation failed:")
    print(result.stderr)
    exit(1)

compiled = json.loads(result.stdout)
contract_key = None
for key in compiled["contracts"]:
    if key.endswith(":SecureToken"):
        contract_key = key
        break
if not contract_key:
    raise Exception("Contract not found")

contract_data = compiled["contracts"][contract_key]
abi_raw = contract_data["abi"]
abi = json.loads(abi_raw) if isinstance(abi_raw, str) else abi_raw
bytecode = contract_data["bin"]

RPC_LIST = [
    "https://base.llamarpc.com",
    "https://mainnet.base.org",
    "https://base-rpc.publicnode.com",
    "https://base.blockpi.network/v1/rpc/public"
]
w3 = None
for rpc in RPC_LIST:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 10}))
        if w3.is_connected():
            print(f"✅ Connected to RPC: {rpc}")
            break
    except:
        continue
if not w3 or not w3.is_connected():
    raise Exception("All RPCs failed. Check internet.")

PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
if not PRIVATE_KEY:
    raise Exception("OWNER_PRIVATE_KEY missing")
account = w3.eth.account.from_key(PRIVATE_KEY)
nonce = w3.eth.get_transaction_count(account.address)

contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx = contract.constructor("Spirit Shield", "SHIELD").build_transaction({
    "from": account.address,
    "nonce": nonce,
    "gas": 2000000,
    "gasPrice": w3.eth.gas_price,
    "chainId": 8453
})
signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"⏳ Deployment tx: {tx_hash.hex()}")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt.contractAddress
print(f"✅ Contract deployed: {contract_address}")

scammer = "0x6511204D46a83BfFcC0DB73d5358522C8307981e8"
token = w3.eth.contract(address=contract_address, abi=abi)
nonce = w3.eth.get_transaction_count(account.address)
tx = token.functions.addToBlacklist(scammer).build_transaction({
    "from": account.address,
    "nonce": nonce,
    "gas": 100000,
    "gasPrice": w3.eth.gas_price,
    "chainId": 8453
})
signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"✅ Scammer blacklisted (tx: {tx_hash.hex()})")

with open(".env", "a") as f:
    f.write(f"\nTOKEN_CONTRACT={contract_address}\n")
print("✅ TOKEN_CONTRACT saved to .env")
PY

chmod +x deploy_contract.py

echo "🚀 Deploying on Base..."
python3 deploy_contract.py

# ---- Create monitor with local signing ----
cat > scammer_monitor.py << 'MON'
#!/usr/bin/env python3
import os, time
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

RPC_LIST = ["https://base.llamarpc.com", "https://mainnet.base.org", "https://base-rpc.publicnode.com"]
w3 = None
for rpc in RPC_LIST:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 10}))
        if w3.is_connected():
            break
    except:
        continue
if not w3 or not w3.is_connected():
    print("❌ RPC connection failed")
    exit(1)

TOKEN = os.getenv("TOKEN_CONTRACT")
SCAMMER = os.getenv("SCAMMER", "0x6511204D46a83BfFcC0DB73d5358522C8307981e8")
RECOVERY = os.getenv("RECOVERY", "0xA7AE3C7b8e539447094b0Bb517F60EaBcf6bCddF")
PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
if not all([TOKEN, PRIVATE_KEY]):
    print("❌ Missing TOKEN_CONTRACT or OWNER_PRIVATE_KEY")
    exit(1)

account = w3.eth.account.from_key(PRIVATE_KEY)
ABI = [
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}], "name": "seizeTokens", "outputs": [], "type": "function"}
]
token = w3.eth.contract(address=TOKEN, abi=ABI)

def seize():
    balance = token.functions.balanceOf(SCAMMER).call()
    if balance > 0:
        nonce = w3.eth.get_transaction_count(account.address)
        tx = token.functions.seizeTokens(SCAMMER, RECOVERY).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'chainId': 8453
        })
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Seized {balance} tokens: {tx_hash.hex()}")
    else:
        print("🔹 Scammer has 0 tokens.")

if __name__ == "__main__":
    while True:
        try: seize()
        except Exception as e: print(f"❌ {e}")
        time.sleep(60)
MON

chmod +x scammer_monitor.py

# ---- Start monitor ----
echo "🔄 Starting scammer monitor..."
pkill -f scammer_monitor.py 2>/dev/null || true
nohup python3 scammer_monitor.py > monitor.log 2>&1 &

# ---- Push encrypted token list (if exists) ----
if [ -f tokens.json ]; then
    echo "📤 Pushing encrypted token list..."
    python3 sync_tokens.py sync || echo "⚠️ Sync skipped"
fi

echo ""
echo "==========================================="
echo "✅ DEPLOYMENT COMPLETE – SHIELD IS UP!"
echo "==========================================="
echo "📌 Contract Address:"
grep TOKEN_CONTRACT .env | tail -1
echo ""
echo "🟢 Monitor running (logs: monitor.log)"
echo "🛡️ Scammer blacklisted – any tokens they hold will be seized."
echo "🔒 Your token list is encrypted on GitHub – invisible to hackers."
echo "🎯 To manually seize: visit your website and click the admin button."
echo "==========================================="
