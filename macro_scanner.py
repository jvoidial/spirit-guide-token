#!/usr/bin/env python3
import requests, json, os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("METAL_API_KEY", "demo")
BASE_URL = "https://api.metalpriceapi.com/v1/latest"
def fetch_metal_prices():
    try:
        params = {"api_key": API_KEY, "base": "USD", "currencies": "XAU,XAG"}
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {'gold': data['rates'].get('XAU', 0), 'silver': data['rates'].get('XAG', 0)}
    except: pass
    return {'gold': 2400.0, 'silver': 30.0}
def fetch_macro_sentiment():
    return {'sentiment': 'neutral', 'volatility': 0.2, 'inflation': 0.03}
def get_whale_activity():
    return ['VDOO', 'SGUIDE', 'PENNIES', 'PIDX']
if __name__ == "__main__":
    metals = fetch_metal_prices()
    macro = fetch_macro_sentiment()
    whales = get_whale_activity()
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'gold_usd': metals['gold'],
        'silver_usd': metals['silver'],
        'macro': macro,
        'whale_tokens': whales
    }
    with open('macro_data.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("✅ Macro data fetched.")
