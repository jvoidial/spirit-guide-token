#!/usr/bin/env python3
import json, subprocess
with open('investment_strategy.json', 'r') as f:
    strategy = json.load(f)
print("📊 Strategy received:", strategy['investment_signals'])
subprocess.run(["python3", "trade_executor.py"])
