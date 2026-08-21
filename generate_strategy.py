#!/usr/bin/env python3
import json, math, os
from datetime import datetime, timezone

try:
    with open('brain_status.json', 'r') as f:
        brain = json.load(f)
    coherence = brain.get('brain', {}).get('coherence', 0.934)
    voxel_energy = brain.get('brain', {}).get('voxel_energy', 0.790)
    temporal_phase = brain.get('brain', {}).get('temporal_phase', 0.794)
except:
    coherence, voxel_energy, temporal_phase = 0.934, 0.790, 0.794

phi = 1.618033988749895
freq = {"PIDX": 1/phi, "SGUIDE": phi, "VDOO": phi**2, "PENNIES": phi**3}
total = sum(freq.values())
raw = {k: v/total for k,v in freq.items()}
cf = 1 + (coherence - 0.5) * 0.5
adj = {k: w*cf if k in ["SGUIDE","VDOO"] else w/cf for k,w in raw.items()}
tot_adj = sum(adj.values())
alloc = {k: v/tot_adj for k,v in adj.items()}

signals = {}
for token in freq:
    if coherence > 0.85 and voxel_energy > 0.7:
        action, conf = "BUY", int((coherence+voxel_energy)/2*100)
    elif coherence < 0.7 or voxel_energy < 0.5:
        action, conf = "SELL", int((1-coherence + 1-voxel_energy)/2*100)
    else:
        action, conf = "HOLD", 70
    signals[token] = {"action": action, "confidence": conf, "allocation": round(alloc[token]*100,2)}

strategy = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "system_state": {"coherence_score": coherence, "voxel_energy": voxel_energy, "temporal_phase": temporal_phase},
    "resonance_frequencies": freq,
    "allocation_weights": alloc,
    "investment_signals": signals,
    "strategy_logic": {
        "buy_condition": f"coherence > 0.85 and voxel_energy > 0.7 (current: {coherence:.2f}, {voxel_energy:.2f})",
        "sell_condition": f"coherence < 0.7 or voxel_energy < 0.5",
        "hold_condition": "otherwise"
    }
}
with open('investment_strategy.json', 'w') as f:
    json.dump(strategy, f, indent=2)
print("✅ Strategy generated.")
