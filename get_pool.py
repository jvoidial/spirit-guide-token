from web3 import Web3
import sys

TOKEN = "0x38e4f08D08b4D772A7B75669C356b4749dd2d30b"
WETH = "0x4200000000000000000000000000000000000006"
FACTORY = "0x8909Dc15e40173Ff4699343b6eb8132c65e18eC6"

# Public RPC for Base (LlamaNodes is free)
rpc = "https://base.llamarpc.com"
w3 = Web3(Web3.HTTPProvider(rpc))

# Factory ABI (only getPair function)
abi = '[{"inputs":[{"name":"token0","type":"address"},{"name":"token1","type":"address"}],"name":"getPair","outputs":[{"name":"pair","type":"address"}],"stateMutability":"view","type":"function"}]'
contract = w3.eth.contract(address=FACTORY, abi=abi)

# Call getPair(TOKEN, WETH) – order doesn't matter
pair = contract.functions.getPair(TOKEN, WETH).call()
if pair == "0x0000000000000000000000000000000000000000":
    # Try reversed
    pair = contract.functions.getPair(WETH, TOKEN).call()
if pair == "0x0000000000000000000000000000000000000000":
    print("ERROR")
    sys.exit(1)
print(pair)
