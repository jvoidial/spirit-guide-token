import requests, json, sys
TOKEN = "0x38e4f08D08b4D772A7B75669C356b4749dd2d30b".lower()
pool = None

endpoints = {
    "uniswap_v3": "https://api.studio.thegraph.com/query/48233/uniswap-v3-base/version/latest",
    "uniswap_v2": "https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-v2-base",
    "sushiswap": "https://api.thegraph.com/subgraphs/name/sushiswap/base"
}

for name, url in endpoints.items():
    if "v3" in name:
        q = f'{{ pool0: pools(where: {{ token0: "{TOKEN}" }}) {{ id }} pool1: pools(where: {{ token1: "{TOKEN}" }}) {{ id }} }}'
    else:
        q = f'{{ pair0: pairs(where: {{ token0: "{TOKEN}" }}) {{ id }} pair1: pairs(where: {{ token1: "{TOKEN}" }}) {{ id }} }}'
    try:
        r = requests.post(url, json={'query': q}, timeout=15)
        data = r.json()
        if 'data' in data:
            items = data['data'].get('pool0', []) + data['data'].get('pool1', [])
            if not items:
                items = data['data'].get('pair0', []) + data['data'].get('pair1', [])
            if items:
                pool = items[0]['id']
                print(pool)
                sys.exit(0)
    except:
        continue
print("ERROR")
sys.exit(1)
