import requests, json, sys

TOKEN = "0x38e4f08D08b4D772A7B75669C356b4749dd2d30b"
WETH = "0x4200000000000000000000000000000000000006"
FACTORY = "0x8909Dc15e40173Ff4699343b6eb8132c65e18eC6"

# Lowercase everything – RPC accepts lowercase hex
t = TOKEN.lower()
w = WETH.lower()
f = FACTORY.lower()

# getPair(address token0, address token1) method ID: 0xe6a43905
# pad both addresses to 32 bytes (64 hex chars)
data = "0xe6a43905" + "000000000000000000000000" + t[2:] + "000000000000000000000000" + w[2:]

payload = {
    "jsonrpc": "2.0",
    "method": "eth_call",
    "params": [{"to": f, "data": data}, "latest"],
    "id": 1
}

rpc = "https://base.llamarpc.com"
resp = requests.post(rpc, json=payload)
result = resp.json().get("result")

if result and result != "0x0000000000000000000000000000000000000000":
    # Extract address (last 40 hex chars)
    pool = "0x" + result[-40:]
    print(pool)
    sys.exit(0)

# Try reversed order (WETH, TOKEN)
data_rev = "0xe6a43905" + "000000000000000000000000" + w[2:] + "000000000000000000000000" + t[2:]
payload_rev = {
    "jsonrpc": "2.0",
    "method": "eth_call",
    "params": [{"to": f, "data": data_rev}, "latest"],
    "id": 2
}
resp_rev = requests.post(rpc, json=payload_rev)
result_rev = resp_rev.json().get("result")
if result_rev and result_rev != "0x0000000000000000000000000000000000000000":
    pool = "0x" + result_rev[-40:]
    print(pool)
    sys.exit(0)

print("ERROR")
sys.exit(1)
