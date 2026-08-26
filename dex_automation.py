#!/usr/bin/env python3
"""
Automated DEX Interactions + Vault Management + Contract Verification
Uniswap V2 on Base – with GitHub Actions ready
"""

import os, sys, time, json, binascii, requests
from web3 import Web3
from dotenv import load_dotenv
from decimal import Decimal, getcontext

getcontext().prec = 30
load_dotenv()

# ---- Configuration ----
RPC = "https://mainnet.base.org"
ROUTER = "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24"   # Uniswap V2 Router
WETH = "0x4200000000000000000000000000000000000006"
VAULT = "0xfAcb5905E1E592D69a2AE0af6F82330c07e4312"    # Pennies Index Vault
BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY")       # for verification

TOKENS = {
    "PENNIES": "0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7",
    "SGUIDE": "0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a",
    "PIDX": "0xa36E026FC453880537e10d21fC139439bD2702fc",
    "VDOO": "0x38e4f08D08b4D772A7B75669C356b4749dd2d30b",
}

VAULT_WEIGHTS = {"PENNIES": 40, "SGUIDE": 30, "VDOO": 20, "WBTC": 10}

# ---- Web3 ----
w3 = Web3(Web3.HTTPProvider(RPC))
if not w3.is_connected():
    print("❌ RPC connection failed.")
    sys.exit(1)

PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
if not PRIVATE_KEY:
    print("❌ OWNER_PRIVATE_KEY not set in .env")
    sys.exit(1)

PRIVATE_KEY = PRIVATE_KEY.strip()
if PRIVATE_KEY.startswith('0x'):
    hex_key = PRIVATE_KEY[2:]
else:
    hex_key = PRIVATE_KEY
try:
    binascii.unhexlify(hex_key)
    if len(hex_key) != 64:
        raise ValueError
except (binascii.Error, ValueError):
    print("❌ Invalid private key (must be 64 hex chars).")
    sys.exit(1)

account = w3.eth.account.from_key(PRIVATE_KEY)
print(f"📍 Wallet: {account.address}")

# ---- ABIs ----
ROUTER_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "type": "function",
        "payable": True
    },
    {
        "constant": False,
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
            {"name": "amountADesired", "type": "uint256"},
            {"name": "amountBDesired", "type": "uint256"},
            {"name": "amountAMin", "type": "uint256"},
            {"name": "amountBMin", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "addLiquidity",
        "outputs": [
            {"name": "amountA", "type": "uint256"},
            {"name": "amountB", "type": "uint256"},
            {"name": "liquidity", "type": "uint256"}
        ],
        "type": "function"
    }
]
router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)

VAULT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "token", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "deposit",
        "outputs": [],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "token", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "type": "function"
    }
]
vault = w3.eth.contract(address=VAULT, abi=VAULT_ABI)

# ---- Helpers ----
def to_wei(amount: Decimal) -> int:
    return int(amount * Decimal(10**18))

def from_wei(wei: int) -> Decimal:
    return Decimal(wei) / Decimal(10**18)

def get_balance(token_addr, wallet_addr):
    abi = [{"constant": True, "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"}]
    token = w3.eth.contract(address=token_addr, abi=abi)
    return token.functions.balanceOf(wallet_addr).call()

def approve_token(token_addr, spender, amount_wei):
    abi = [{"constant": False, "inputs": [{"name": "spender", "type": "address"},
                                           {"name": "amount", "type": "uint256"}],
            "name": "approve", "outputs": [{"name": "", "type": "bool"}],
            "type": "function"}]
    token = w3.eth.contract(address=token_addr, abi=abi)
    nonce = w3.eth.get_transaction_count(account.address)
    tx = token.functions.approve(spender, amount_wei).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 100000,
        "gasPrice": w3.eth.gas_price,
        "chainId": 8453
    })
    try:
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        return receipt.status == 1
    except Exception as e:
        print(f"Approval failed: {e}")
        return False

def send_and_wait(tx_builder):
    nonce = w3.eth.get_transaction_count(account.address)
    tx = tx_builder(nonce)
    if 'gas' not in tx or tx['gas'] == 0:
        try:
            tx['gas'] = w3.eth.estimate_gas(tx)
        except Exception as e:
            print(f"Gas estimation failed: {e}")
            tx['gas'] = 500000
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    return receipt

# ---- DEX functions ----
def swap_eth_for_token(token_addr, amount_eth: Decimal):
    print(f"🔄 Swapping {amount_eth} ETH for token...")
    amount_in = to_wei(amount_eth)
    path = [WETH, token_addr]
    def build(nonce):
        return router.functions.swapExactETHForTokens(
            0, path, account.address, int(time.time())+600
        ).build_transaction({
            "from": account.address,
            "value": amount_in,
            "nonce": nonce,
            "gas": 250000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 8453
        })
    receipt = send_and_wait(build)
    if receipt.status == 1:
        print(f"✅ Swap successful! Tx: {receipt.transactionHash.hex()}")
    else:
        print("❌ Swap failed.")

def swap_token_for_eth(token_addr, amount_token: Decimal):
    print(f"🔄 Swapping {amount_token} token for ETH...")
    amount_in = to_wei(amount_token)
    path = [token_addr, WETH]
    if not approve_token(token_addr, ROUTER, amount_in):
        print("❌ Approval failed.")
        return
    def build(nonce):
        return router.functions.swapExactTokensForETH(
            amount_in, 0, path, account.address, int(time.time())+600
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 250000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 8453
        })
    receipt = send_and_wait(build)
    if receipt.status == 1:
        print(f"✅ Swap successful! Tx: {receipt.transactionHash.hex()}")
    else:
        print("❌ Swap failed.")

def add_liquidity(token_addr, amount_token: Decimal, amount_eth: Decimal):
    print(f"🔄 Adding liquidity: {amount_token} token + {amount_eth} ETH")
    amount_token_wei = to_wei(amount_token)
    amount_eth_wei = to_wei(amount_eth)
    if not approve_token(token_addr, ROUTER, amount_token_wei):
        print("❌ Approval failed.")
        return
    def build(nonce):
        return router.functions.addLiquidity(
            token_addr, WETH,
            amount_token_wei, amount_eth_wei,
            0, 0,
            account.address,
            int(time.time())+600
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 350000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 8453
        })
    receipt = send_and_wait(build)
    if receipt.status == 1:
        print(f"✅ Liquidity added! Tx: {receipt.transactionHash.hex()}")
    else:
        print("❌ Liquidity addition failed.")

def check_balance(token_symbol):
    addr = TOKENS.get(token_symbol)
    if not addr:
        print(f"❌ Unknown token: {token_symbol}")
        return
    bal = get_balance(addr, account.address)
    print(f"💰 {token_symbol} balance: {from_wei(bal):.6f}")

# ---- Vault functions ----
def vault_deposit(token_symbol, amount: Decimal):
    token_addr = TOKENS.get(token_symbol)
    if not token_addr:
        print(f"❌ Unknown token: {token_symbol}")
        return
    amount_wei = to_wei(amount)
    if not approve_token(token_addr, VAULT, amount_wei):
        print("❌ Approval failed.")
        return
    def build(nonce):
        return vault.functions.deposit(token_addr, amount_wei).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 250000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 8453
        })
    receipt = send_and_wait(build)
    if receipt.status == 1:
        print(f"✅ Deposit successful! Tx: {receipt.transactionHash.hex()}")
    else:
        print("❌ Deposit failed.")

def vault_withdraw(token_symbol, amount: Decimal):
    token_addr = TOKENS.get(token_symbol)
    if not token_addr:
        print(f"❌ Unknown token: {token_symbol}")
        return
    amount_wei = to_wei(amount)
    def build(nonce):
        return vault.functions.withdraw(token_addr, amount_wei).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 250000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 8453
        })
    receipt = send_and_wait(build)
    if receipt.status == 1:
        print(f"✅ Withdrawal successful! Tx: {receipt.transactionHash.hex()}")
    else:
        print("❌ Withdrawal failed.")

def vault_info():
    print(f"\n🏦 Pennies Index Vault")
    print(f"   Address: {VAULT}")
    print("   Weighted basket:")
    for token, weight in VAULT_WEIGHTS.items():
        print(f"     - {token}: {weight}%")

# ---- Contract Verification via BaseScan ----
def verify_contract(contract_address, contract_name, source_code, constructor_args=""):
    if not BASESCAN_API_KEY:
        print("❌ BASESCAN_API_KEY not set. Cannot verify.")
        return
    url = "https://api.basescan.org/api"
    params = {
        "module": "contract",
        "action": "verifysourcecode",
        "apikey": BASESCAN_API_KEY,
        "contractaddress": contract_address,
        "sourceCode": source_code,
        "codeformat": "solidity-single-file",
        "contractname": contract_name,
        "compilerversion": "v0.8.19+commit.7e4a7e8e",
        "optimizationUsed": "1",
        "runs": "200",
        "constructorArguments": constructor_args,
        "evmversion": "london"
    }
    try:
        resp = requests.post(url, data=params, timeout=30)
        result = resp.json()
        if result.get("status") == "1":
            print(f"✅ Verification submitted. GUID: {result.get('result')}")
        else:
            print(f"❌ Verification failed: {result.get('result')}")
    except Exception as e:
        print(f"❌ API request error: {e}")

# ---- Main menu ----
if __name__ == "__main__":
    while True:
        print("\n🤖 Automated DEX & Vault Script")
        print("================================")
        print("1. Swap ETH → Token")
        print("2. Swap Token → ETH")
        print("3. Add Liquidity")
        print("4. Check Token Balance")
        print("5. Vault Actions")
        print("6. Verify a Contract (BaseScan)")
        print("7. Exit")
        choice = input("Select option: ")
        if choice == "1":
            token = input("Token symbol (PENNIES, SGUIDE, PIDX, VDOO): ").upper()
            addr = TOKENS.get(token)
            if not addr:
                print("Invalid token.")
                continue
            amount_eth = Decimal(input("Amount of ETH to swap: "))
            swap_eth_for_token(addr, amount_eth)
        elif choice == "2":
            token = input("Token symbol: ").upper()
            addr = TOKENS.get(token)
            if not addr:
                print("Invalid token.")
                continue
            amount_token = Decimal(input("Amount of token to swap: "))
            swap_token_for_eth(addr, amount_token)
        elif choice == "3":
            token = input("Token symbol: ").upper()
            addr = TOKENS.get(token)
            if not addr:
                print("Invalid token.")
                continue
            amount_token = Decimal(input("Amount of token: "))
            amount_eth = Decimal(input("Amount of ETH: "))
            add_liquidity(addr, amount_token, amount_eth)
        elif choice == "4":
            token = input("Token symbol: ").upper()
            check_balance(token)
        elif choice == "5":
            print("\n🏦 Vault Actions")
            print("1. Deposit tokens into vault")
            print("2. Withdraw tokens from vault")
            print("3. View vault info")
            sub = input("Select action: ")
            if sub == "1":
                token = input("Token symbol to deposit: ").upper()
                amount = Decimal(input("Amount: "))
                vault_deposit(token, amount)
            elif sub == "2":
                token = input("Token symbol to withdraw: ").upper()
                amount = Decimal(input("Amount: "))
                vault_withdraw(token, amount)
            elif sub == "3":
                vault_info()
            else:
                print("Invalid option.")
        elif choice == "6":
            addr = input("Contract address: ")
            name = input("Contract name (e.g., MyToken): ")
            print("Paste the full source code (end with Ctrl+D on new line):")
            lines = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                lines.append(line)
            source = "\n".join(lines)
            if source.strip():
                verify_contract(addr, name, source)
            else:
                print("No source provided.")
        elif choice == "7":
            print("Exiting.")
            break
        else:
            print("Invalid option.")
