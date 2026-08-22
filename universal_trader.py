#!/usr/bin/env python3
import json, os, time, math, sys
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SIMULATION = (not PRIVATE_KEY or PRIVATE_KEY == "your_private_key_here")

# ----- CONFIG -----
RPC = "https://base.llamarpc.com"
ROUTER = "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24"
WETH = "0x4200000000000000000000000000000000000006"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
TOKENS = {
    "SGUIDE": "0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a",
    "VDOO": "0x38e4f08D08b4D772A7B75669C356b4749dd2d30b",
    "PENNIES": "0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7",
    "PIDX": "0xa36E026FC453880537e10d21fC139439bD2702fc",
    "USDC": USDC
}
DECIMALS = {"USDC": 6, "SGUIDE": 18, "VDOO": 18, "PENNIES": 18, "PIDX": 18}
SLIPPAGE = 0.05
MAX_GAS_PRICE_GWEI = 20

ROUTER_ABI = [
    {"constant": True, "inputs": [{"name": "amountIn", "type": "uint256"}, {"name": "path", "type": "address[]"}], "name": "getAmountsOut", "outputs": [{"name": "amounts", "type": "uint256[]"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "amountOutMin", "type": "uint256"}, {"name": "path", "type": "address[]"}, {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}], "name": "swapExactETHForTokens", "outputs": [{"name": "amounts", "type": "uint256[]"}], "type": "function", "payable": True},
    {"constant": False, "inputs": [{"name": "amountIn", "type": "uint256"}, {"name": "amountOutMin", "type": "uint256"}, {"name": "path", "type": "address[]"}, {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}], "name": "swapExactTokensForETH", "outputs": [{"name": "amounts", "type": "uint256[]"}], "type": "function"}
]
ERC20_ABI = [
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
]

if not SIMULATION:
    w3 = Web3(Web3.HTTPProvider(RPC))
    if not w3.is_connected():
        raise Exception("RPC not connected")
    account = w3.eth.account.from_key(PRIVATE_KEY)
    router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)

def get_min_amount_out(amount_in, path):
    try:
        amounts = router.functions.getAmountsOut(amount_in, path).call()
        expected = amounts[-1]
        return int(expected * (1 - SLIPPAGE))
    except Exception as e:
        print(f"⚠️  Quote error: {e}")
        return 0

def check_gas():
    if SIMULATION: return True
    gas_price = w3.eth.gas_price
    if gas_price / 1e9 > MAX_GAS_PRICE_GWEI:
        print(f"⚠️  Gas price {gas_price/1e9:.1f} Gwei > {MAX_GAS_PRICE_GWEI} – skipping.")
        return False
    return True

def execute_buy(token_addr, amount_eth=0.001):
    if SIMULATION:
        print(f"🔸 SIMULATE BUY {amount_eth} ETH -> {token_addr}")
        return None
    if not check_gas():
        return None
    balance = w3.eth.get_balance(account.address)
    amount_in_wei = int(amount_eth * 10**18)
    if balance < amount_in_wei:
        print(f"❌ Insufficient ETH: {Web3.from_wei(balance,'ether')} < {amount_eth}")
        return None
    path = [WETH, token_addr]
    min_out = get_min_amount_out(amount_in_wei, path)
    deadline = int(time.time()) + 300
    nonce = w3.eth.get_transaction_count(account.address)
    tx = router.functions.swapExactETHForTokens(
        min_out, path, account.address, deadline
    ).build_transaction({
        'from': account.address,
        'value': amount_in_wei,
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
        'chainId': 8453
    })
    signed = account.sign_transaction(tx)
    return w3.eth.send_raw_transaction(signed.rawTransaction).hex()

def execute_sell(token_addr, amount_token, token_name):
    if SIMULATION:
        print(f"🔸 SIMULATE SELL {amount_token} of {token_name}")
        return None
    if not check_gas():
        return None
    token_contract = w3.eth.contract(address=token_addr, abi=ERC20_ABI)
    approve_tx = token_contract.functions.approve(ROUTER, amount_token).build_transaction({
        'from': account.address,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': 8453
    })
    signed_approve = account.sign_transaction(approve_tx)
    approve_hash = w3.eth.send_raw_transaction(signed_approve.rawTransaction)
    w3.eth.wait_for_transaction_receipt(approve_hash)
    print(f"✅ Approved {token_name}")

    path = [token_addr, WETH]
    min_out = get_min_amount_out(amount_token, path)
    deadline = int(time.time()) + 300
    nonce = w3.eth.get_transaction_count(account.address)
    tx = router.functions.swapExactTokensForETH(
        amount_token, min_out, path, account.address, deadline
    ).build_transaction({
        'from': account.address,
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
        'chainId': 8453
    })
    signed = account.sign_transaction(tx)
    return w3.eth.send_raw_transaction(signed.rawTransaction).hex()

def get_token_balance(token_addr):
    if SIMULATION:
        return 1000 * 10**18
    contract = w3.eth.contract(address=token_addr, abi=ERC20_ABI)
    return contract.functions.balanceOf(account.address).call()

if __name__ == "__main__":
    try:
        with open('investment_strategy.json', 'r') as f:
            strategy = json.load(f)
    except FileNotFoundError:
        print("❌ No strategy file.")
        sys.exit(1)

    signals = strategy.get('investment_signals', {})
    for token, signal in signals.items():
        if token not in TOKENS:
            continue
        addr = TOKENS[token]
        action = signal['action']
        if action == "BUY":
            amt_eth = 0.001
            tx = execute_buy(addr, amt_eth)
            if tx:
                print(f"✅ BUY {token}: https://basescan.org/tx/{tx}")
        elif action == "SELL":
            balance = get_token_balance(addr)
            if balance > 0:
                sell_amount = int(balance * 0.5)
                if sell_amount > 0:
                    tx = execute_sell(addr, sell_amount, token)
                    if tx:
                        print(f"✅ SELL {token}: https://basescan.org/tx/{tx}")
        else:
            print(f"⏭️ HOLD {token}")
