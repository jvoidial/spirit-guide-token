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
