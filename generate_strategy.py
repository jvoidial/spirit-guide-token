#!/usr/bin/env python3
import json, math, os
from datetime import datetime, timezone
coherence = 0.95
voxel_energy = 0.85
temporal_phase = 0.794
phi = 1.618033988749895
freq = {"PIDX": 1/phi, "SGUIDE": phi, "VDOO": phi**2, "PENNIES": phi**3, "GOLD": 0.5, "SILVER": 0.4, "USDC": 0.3}
total = sum(freq.values())
raw = {k: v/total for k,v in freq.items()}
cf = 1 + (coherence - 0.5)*0.5
adj = {}
for k,w in raw.items():
    if k in ["SGUIDE","VDOO","PIDX","PENNIES"]:
        adj[k] = w * cf
    elif k in ["GOLD","SILVER"]:
        adj[k] = w * (1 + (1 - coherence)*0.2)
    else:
        adj[k] = w
tot_adj = sum(adj.values())
alloc = {k: v/tot_adj for k,v in adj.items()}
signals = {}
for token in freq:
    if token in ["SGUIDE","VDOO","PIDX","PENNIES"]:
        action, conf = "BUY", 95
    else:
        action, conf = "HOLD", 50
    signals[token] = {"action": action, "confidence": conf, "allocation": round(alloc.get(token,0)*100,2)}
strategy = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "system_state": {"coherence_score": coherence, "voxel_energy": voxel_energy, "temporal_phase": temporal_phase},
    "macro": {"gold_usd": 2400, "silver_usd": 30, "sentiment": "neutral"},
    "resonance_frequencies": freq,
    "allocation_weights": alloc,
    "investment_signals": signals,
    "strategy_logic": {
        "buy_condition": "forced for testing",
        "sell_condition": "none",
        "hold_condition": "otherwise"
    }
}
with open('investment_strategy.json', 'w') as f:
    json.dump(strategy, f, indent=2)
print("✅ Strategy with forced BUY signals.")
