import json, time, sys, requests
from collections import defaultdict
from web3 import Web3

RPC = "https://mainnet.base.org"
PK = "1955255138c5f0a45e71fe6efb6f81d9c8ea83058f0795c3d5f9623c7dc3498a"
DEPLOYER = "0x3212D08f2ad637918bd90932829159874E39bE4c"
TOKEN_ADDR = sys.argv[1]
API_KEY = sys.argv[2]
TOKENS = sys.argv[3:]

w3 = Web3(Web3.HTTPProvider(RPC))
account = w3.eth.account.from_key(PK)

def fetch_holders(token_addr):
    url = f"https://api.basescan.org/api?module=token&action=tokenholderlist&contractaddress={token_addr}&apikey={API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    if data['status'] != '1':
        print(f"Error fetching holders for {token_addr}: {data.get('message', 'Unknown error')}")
        return {}
    holders = {}
    for item in data['result']:
        addr = Web3.to_checksum_address(item['TokenHolderAddress'])
        bal = int(item['TokenHolderQuantity'])
        if bal > 0:
            holders[addr] = holders.get(addr, 0) + bal
    return holders

combined = defaultdict(int)
for token in TOKENS:
    print(f"Fetching holders for {token[:10]}...")
    holders = fetch_holders(token)
    for addr, bal in holders.items():
        combined[addr] += bal
    time.sleep(0.5)

total_combined = sum(combined.values())
if total_combined == 0:
    print("No holders found. Skipping airdrop.")
    sys.exit(0)

# Airdrop 10% of total supply
AIRDROP_SUPPLY = 0.10 * 1_000_000_000 * 10**18
erc20_abi = [
    {"constant":False,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}
]
contract = w3.eth.contract(address=TOKEN_ADDR, abi=erc20_abi)

nonce = w3.eth.get_transaction_count(DEPLOYER, "pending")
for addr, bal in combined.items():
    share = bal / total_combined
    amount = int(share * AIRDROP_SUPPLY)
    if amount == 0:
        continue
    tx = contract.functions.transfer(addr, amount).build_transaction({
        "from": DEPLOYER,
        "gas": 100000,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
        "chainId": 8453,
    })
    signed = account.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or getattr(signed, "rawTransaction")
    tx_hash = w3.eth.send_raw_transaction(raw)
    print(f"Sent {amount/1e18:.2f} PIDX to {addr[:10]}... TX: {tx_hash.hex()[:10]}")
    nonce += 1
    time.sleep(0.5)
print("✅ Airdrop complete!")
